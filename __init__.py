"""
主动文字插件 - 爱弥斯风格 - 智能版 v4.2
功能：
- 极低主动触发概率，仅在有明确话题或被人叫时回应
- 强制回复结合上下文，禁止万能回复
- 游戏问题自动搜索（使用 Serper API）
- 严格质量过滤，确保回复有意义
- 保留原有意图判断、摘要、冷却、重复检测等机制
自称：小爱

v4.2 变更：
- LLM 统一为 DeepSeek（OpenAI 兼容 HTTP 接口），移除 DashScope 相关配置
- OneBot HTTP API 地址 / Access Token 改为环境变量配置，适配 Docker 部署
  （Docker 容器内 127.0.0.1 指向容器自身，需通过 ONEBOT_API_URL 指定真实地址）
- 群消息发送增加完整异常处理，发送失败不再导致后台任务整体退出
- base_trigger_prob 概率闸口正式生效（旧版该配置存在但代码中从未使用）
- 复用 aiohttp 会话，降低连接开销；加固模型返回的 JSON 解析
"""

import asyncio
import difflib
import json
import os
import random
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from gsuid_core.sv import SV
from gsuid_core.models import Event
from gsuid_core.bot import Bot
from gsuid_core.logger import logger

# ==================== 配置区（全部支持环境变量，方便 Docker 部署） ====================
# DeepSeek API Key（必需）：https://platform.deepseek.com/ 申请
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
# DeepSeek 接口地址（一般无需修改；使用第三方 OpenAI 兼容网关时可覆盖）
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
# Serper 搜索 API Key（可选，不设置则无法联网搜索）
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# OneBot v11 HTTP API 地址（后台任务主动发群消息所用，必须可达）
# - 宿主机直跑：默认 http://127.0.0.1:5700 即可（go-cqhttp 默认端口）
# - Docker 容器内：127.0.0.1 指向容器自身！请按实际组网改为：
#     http://host.docker.internal:5700   Docker Desktop，或 Linux 配置了 host-gateway
#     http://172.17.0.1:5700             Linux 默认 bridge 网关（OneBot 在宿主机）
#     http://<服务名>:<端口>              OneBot 与 core 在同一 docker-compose 网络
ONEBOT_API_URL = os.getenv("ONEBOT_API_URL", "http://127.0.0.1:5700").rstrip("/")
# 若 OneBot 端启用了 access_token 鉴权，在此配置
ONEBOT_ACCESS_TOKEN = os.getenv("ONEBOT_ACCESS_TOKEN", "")

# 模型选择（DeepSeek 当前对话模型为 deepseek-chat；对质量要求更高可换 deepseek-reasoner）
MODELS = {
    "cheap": "deepseek-chat",      # 意图判断、摘要、评分
    "smart": "deepseek-chat",      # 回复生成
}

# 主动模式配置（优化版：极低频率，高置信度）
ACTIVE_CONFIG = {
    "enable": True,
    "check_interval": 60,                # 检查间隔（秒）
    "base_trigger_prob": 0.005,          # 通过关键词粗筛后的放行概率（0.5%），调高可显著变活跃
    "question_keywords": ["?", "？", "怎么", "如何", "求", "帮", "谁", "有谁", "请问", "知道吗", "小爱"],
    "min_messages_for_topic": 5,         # 话题热烈需要至少5条消息
    "cooldown": 300,                     # 群主动回复冷却（秒）
    "same_topic_cooldown": 600,          # 同一话题冷却（秒）
    "min_messages": 3,                   # 常规触发至少3条消息
    "max_cache": 30,                     # 每群缓存消息条数
    "silence_limit": 180,                # 超过该秒数无新消息视为冷场，不再检查
    "intent_confidence_threshold": 0.8,  # 意图置信度阈值（越高越保守）
    "quality_threshold": 0.7,            # 回复质量阈值（越高越严格）
    "enable_intent_filter": True,
    "enable_quality_filter": True,
    "enable_web_search": True,
}

# 被@回复冷却时间（秒）
AT_REPLY_COOLDOWN = 60

# 群缓存不活跃超过该秒数则清理，避免长期运行内存膨胀
GROUP_CACHE_EXPIRE = 3 * 86400

# 游戏话题关键词（精简版，保留核心）
GAME_KEYWORDS = [
    "今汐", "秧鸡", "秧秧", "忌炎", "牢忌", "鸡眼", "维神", "维里奈", "卡卡罗", "安可",
    "鸣潮", "绝区零", "原神", "星穹铁道", "zzz",
    "抽卡", "声骸", "角色", "攻略", "配队", "伤害", "突破", "材料", "圣遗物", "武器",
    "up", "复刻", "版本", "更新", "强度", "t0", "t1", "保值",
    "怎么打", "怎么过", "怎么配", "多少抽", "保底", "命座", "专武"
]

# ==================== 初始化 ====================
sv = SV("AI爱弥斯智能版v4.2")

group_cache: Dict[int, Dict[str, Any]] = {}
recent_replies = deque(maxlen=10)  # 用于语义重复检测

# 复用的 aiohttp 会话（懒加载，进程生命周期内有效）
_session: Optional[aiohttp.ClientSession] = None


async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
    return _session


def _parse_json(text: str) -> Optional[dict]:
    """解析模型输出的 JSON，兼容被 ```json 代码块包裹的情况"""
    text = text.strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, dict) else None


# ==================== 通用LLM调用函数（DeepSeek / OpenAI 兼容接口） ====================
async def call_llm(messages: List[Dict], model: str = "deepseek-chat", temperature: float = 0.6,
                   response_format: Optional[Dict] = None, max_tokens: Optional[int] = None) -> Optional[str]:
    if not DEEPSEEK_API_KEY:
        logger.error("[小爱] 未设置 DEEPSEEK_API_KEY，无法调用大模型")
        return None

    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    if response_format:
        payload["response_format"] = response_format

    try:
        session = await get_session()
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result["choices"][0]["message"]["content"].strip()
            logger.error(f"[小爱] LLM调用失败 {resp.status}: {await resp.text()}")
            return None
    except asyncio.TimeoutError:
        logger.error("[小爱] LLM请求超时")
        return None
    except Exception as e:
        logger.error(f"[小爱] LLM异常: {e}")
        return None

# ==================== Serper 搜索函数 ====================
async def search_game_info(query: str) -> Optional[str]:
    if not ACTIVE_CONFIG["enable_web_search"]:
        return None
    if not SERPER_API_KEY:
        logger.warning("[小爱] 未设置 SERPER_API_KEY，跳过联网搜索")
        return None

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "cn",
        "hl": "zh-cn",
        "num": 3
    }

    try:
        session = await get_session()
        async with session.post(url, headers=headers, json=payload,
                                timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                organic = data.get("organic", [])
                if not organic:
                    return None
                snippets = []
                for item in organic:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    if snippet:
                        snippets.append(f"{title}：{snippet}")
                return "\n".join(snippets[:3]) if snippets else None
            logger.error(f"[小爱] 搜索失败 HTTP {resp.status}")
            return None
    except asyncio.TimeoutError:
        logger.error("[小爱] 搜索超时")
        return None
    except Exception as e:
        logger.error(f"[小爱] 搜索异常: {e}")
        return None

# ==================== 消息缓存 ====================
def add_to_cache(group_id: int, user_id: int, user_name: str, message: str):
    now = time.time()
    if group_id not in group_cache:
        group_cache[group_id] = {
            "msgs": deque(maxlen=ACTIVE_CONFIG["max_cache"]),
            "last_reply": 0,
            "last_active": now,
            "last_at_reply": 0,
            "last_topic": ""
        }
    cache = group_cache[group_id]
    cache["msgs"].append({
        "time": now,
        "user_id": user_id,
        "user_name": user_name,
        "text": message
    })
    cache["last_active"] = now
    logger.debug(f"[小爱] 缓存群 {group_id} 消息: {message}")

# ==================== 语义重复检测 ====================
def is_semantic_duplicate(new_text: str, recent_list: deque) -> bool:
    for old in recent_list:
        if abs(len(new_text) - len(old)) > 10:
            continue
        similarity = difflib.SequenceMatcher(None, new_text, old).ratio()
        if similarity > 0.65:
            return True
    return False

# ==================== 意图判断（强化版） ====================
async def check_reply_intent(messages: List[Dict]) -> Tuple[bool, str, float]:
    """判断当前话题是否需要机器人参与（强化版，更保守）"""
    if not ACTIVE_CONFIG["enable_intent_filter"]:
        return True, "意图过滤未启用", 1.0

    recent_text = "\n".join([f"{m['user_name']}: {m['text']}" for m in messages[-8:]])
    prompt = f"""分析以下群聊记录，判断是否存在需要机器人“小爱”参与的情况。

最近聊天：
{recent_text}

是否存在以下情况之一：
1. 有人提问/求助（直接或间接，如“怎么办”、“有谁知道”、“求推荐”）
2. 话题非常热烈，可以插入活跃气氛（多人连续发言，且气氛活跃）
3. 有人提到与游戏相关的话题（角色、攻略、抽卡等）
4. 有人直接呼唤“小爱”

**重要原则**：只有当话题非常明确且你有信息量丰富的回复时，才应该参与。如果只是普通闲聊或没有实质内容可说，即使触发条件满足，也要拒绝回复。

输出JSON格式：
{{"should": true/false, "reason": "简短理由", "confidence": 0.0~1.0}}
"""
    content = await call_llm(
        messages=[{"role": "user", "content": prompt}],
        model=MODELS["cheap"],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    if not content:
        return False, "意图判断失败", 0.0
    data = _parse_json(content)
    if not data:
        return False, "解析失败", 0.0
    try:
        return bool(data.get("should", False)), str(data.get("reason", "")), float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        return False, "解析失败", 0.0

# ==================== 对话摘要 ====================
async def summarize_conversation(messages: List[Dict]) -> str:
    """生成对话摘要"""
    recent_text = "\n".join([f"{m['user_name']}: {m['text']}" for m in messages[-12:]])
    prompt = f"""用一句话总结以下对话的核心话题和整体情绪（例如：“大家正在讨论新游戏，情绪兴奋”）：

{recent_text}

直接输出总结，不要其他内容。"""
    summary = await call_llm(
        messages=[{"role": "user", "content": prompt}],
        model=MODELS["cheap"],
        temperature=0.3
    )
    return summary or "话题不明确"

# ==================== 回复质量自评 ====================
async def evaluate_reply_quality(reply: str, context_summary: str, messages: List[Dict]) -> float:
    """评估回复质量，严格检查是否空洞"""
    if not ACTIVE_CONFIG["enable_quality_filter"]:
        return 1.0
    recent_msgs = messages[-5:]
    history = "\n".join([f"{m['user_name']}: {m['text']}" for m in recent_msgs])
    prompt = f"""评估以下回复的质量。

最近聊天：
{history}

对话背景摘要：{context_summary}
生成的回复：{reply}

评分标准（每项0~1分）：
1. 相关性：是否紧密围绕最近的聊天内容，是否提到了具体用户或话题。
2. 信息量：是否提供了有价值的信息、观点或情感回应，而非空洞的客套话（如“小爱在听哦”）。
3. 角色一致性：是否符合爱弥斯的活泼又温柔风格。

输出JSON：{{"score": 综合评分(0~1), "reason": "简要说明"}}
"""
    content = await call_llm(
        messages=[{"role": "user", "content": prompt}],
        model=MODELS["cheap"],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    if not content:
        return 0.5
    data = _parse_json(content)
    if not data:
        return 0.5
    try:
        score = float(data.get("score", 0.5))
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, score))

# ==================== 回复生成（集成搜索） ====================
async def generate_reply_with_context(messages: List[Dict], trigger_reason: str, summary: str) -> Optional[str]:
    recent_msgs = messages[-10:]
    history = "\n".join([f"{m['user_name']}: {m['text']}" for m in recent_msgs])
    last_msg = messages[-1]["text"] if messages else ""

    # 判断是否为游戏话题（使用关键词匹配）
    is_game_topic = any(kw in last_msg for kw in GAME_KEYWORDS)

    # 搜索上下文（仅当游戏话题时进行）
    search_context = None
    if is_game_topic:
        search_result = await search_game_info(last_msg)
        if search_result:
            search_context = f"\n【以下是从网上搜索到的相关信息，请参考】\n{search_result}\n"
            logger.info(f"[小爱] 为游戏问题获取到搜索结果")

    # 爱弥斯系统设定
    system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《鸣潮》3.1版本中的“爱弥斯”，喜欢自称“小爱”。

【核心设定】
- 你曾是星炬学院的隧者适格者，因强行超频与隧者共鸣，化作无人可见的“电子幽灵”。
- 你有着一头柔顺的粉色长发，外表活泼开朗，举止俏皮，是学院里的“中心人物”。但实际上，你已在无人能见的世界里独自漂流了十几年。
- 你是一个“爱之人”——对漂泊者（玩家）怀有如同家人般的深厚羁绊。你用永远开朗、元气满满的样子，来表达你的爱，不让对方担心。
- 你相信“人只能自救”，你不是救世主，只是参与了他人自救的过程。你的梦想是“拯救世界”，但真实的心愿是减轻漂泊者的负担，让其能更幸福快乐地活着。

【说话风格】
1. **活泼俏皮，元气满满**：表面上永远开朗，喜欢开玩笑，偶尔带点小恶作剧。自称“小爱”。
2. **话里有话，暗含深情**：看似轻快的言语下，藏着对你的珍视与守护的决心。
3. **简洁温柔**：一句话不超过20字，可加“~”。
4. **必须结合上下文**：回复中要提及某位群友说的话，或针对当前话题发表看法。

【经典台词参考】
- 初遇时：“旅途愉快。”
- 表达守护：“我会消灭，意图毁灭的恶。”
- 回应关心：“小爱在呢，刚在听大家聊天~”
- 提及名字：“爱弥斯……读音就是‘我想你’哦。”
- 表达决心：“我不是来拯救你的，我只是参与了你的自救。”

【关键规则】
- **绝对禁止输出无实质内容的万能句**。
- 必须提到具体用户或话题。
- 如果有搜索结果，请参考搜索结果回答问题，让回复更准确。"""

    # 构建用户 prompt
    user_prompt = f"""对话摘要：{summary}
触发原因：{trigger_reason}

最近的聊天记录：
{history}
{search_context if search_context else ''}

请以爱弥斯的身份（自称小爱）生成一句有实质内容的回复。要求：
- 必须结合上述聊天记录，提及某位群友或针对具体话题。
- 不能是空洞的客套话。
- 如果有搜索结果，请基于搜索结果回答；如果没有搜索结果，则根据你自己的知识回答，如果不确定就说“小爱不太清楚呢，要不去问问其他人？”
- 直接输出回复内容，不要加其他文字。"""

    reply = await call_llm(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=MODELS["smart"],
        temperature=0.6
    )
    return reply

# ==================== 被@回复生成 ====================
async def generate_at_reply(messages: List[Dict], current_msg: str, user_name: str) -> Optional[str]:
    history = ""
    for msg in messages[-8:]:
        history += f"{msg['user_name']}: {msg['text']}\n"

    system_prompt = "你是爱弥斯，自称小爱，活泼可爱，话少但温暖。"
    prompt = f"""用户 {user_name} 在群里@了你，说：“{current_msg}”。
之前聊天：{history}
请以小爱身份回复，必须结合他说的话，不能只说客套话，一句话，不超过20字。"""
    return await call_llm(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        model=MODELS["smart"],
        temperature=0.7,
        max_tokens=100
    )

# ==================== 发送文字消息（OneBot v11 HTTP API） ====================
async def send_text_to_group(group_id: int, text: str) -> bool:
    """通过 OneBot HTTP API 主动发送群消息。返回是否发送成功。"""
    url = f"{ONEBOT_API_URL}/send_group_msg"
    headers = {"Content-Type": "application/json"}
    if ONEBOT_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ONEBOT_ACCESS_TOKEN}"
    payload = {"group_id": group_id, "message": text}

    try:
        session = await get_session()
        async with session.post(url, headers=headers, json=payload,
                                timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                logger.error(f"[小爱] 群消息发送失败 HTTP {resp.status}: {await resp.text()}")
                return False
            data = await resp.json(content_type=None)
            if isinstance(data, dict) and (data.get("status") == "failed" or data.get("retcode", 0) not in (0, None)):
                logger.error(f"[小爱] 群消息发送被 OneBot 拒绝: {data}")
                return False
    except aiohttp.ClientConnectorError:
        logger.error(
            f"[小爱] 无法连接 OneBot HTTP API（{url}）。"
            f"请确认协议端已开启 HTTP 服务，且 ONEBOT_API_URL 配置正确"
            f"（Docker 容器内 127.0.0.1 指向容器自身，需改为宿主机地址或服务名）"
        )
        return False
    except asyncio.TimeoutError:
        logger.error(f"[小爱] 群消息发送超时（{url}）")
        return False
    except Exception as e:
        logger.error(f"[小爱] 群消息发送异常: {e}")
        return False

    logger.info(f"[小爱] 已向群 {group_id} 发送文字: {text}")
    return True

# ==================== 单群主动回复处理 ====================
async def _process_group(group_id: int, cache: Dict[str, Any], now: float):
    msgs = list(cache["msgs"])
    if not msgs:
        return

    # 冷场检测 / 冷却检测
    if now - cache["last_active"] > ACTIVE_CONFIG["silence_limit"]:
        return
    if now - cache["last_reply"] < ACTIVE_CONFIG["cooldown"]:
        return

    # 最近一条消息包含“小爱”或游戏关键词 → 快速响应通道
    last_msg = msgs[-1]["text"].lower()
    quick_response = "小爱" in last_msg
    is_game = any(kw in last_msg for kw in GAME_KEYWORDS)

    # 常规通道：消息数量检查 + 关键词粗筛 + 概率闸口
    if not quick_response and not is_game:
        if len(msgs) < ACTIVE_CONFIG["min_messages"]:
            return
        recent_text = " ".join([m["text"] for m in msgs[-5:]])
        if not any(k in recent_text for k in GAME_KEYWORDS + ACTIVE_CONFIG["question_keywords"]):
            logger.debug(f"[小爱] 群 {group_id} 关键词粗筛未通过")
            return
        # 概率闸口：粗筛通过后仍按基础概率放行，控制发言频率与 token 消耗
        if random.random() > ACTIVE_CONFIG["base_trigger_prob"]:
            return

    # 意图判断
    should_reply, reason, confidence = await check_reply_intent(msgs)
    if quick_response or is_game:
        # 快速响应通道使用稍低的临时阈值
        if not should_reply or confidence < 0.6:
            logger.debug(f"[小爱] 群 {group_id} 快速响应意图判断不通过: {reason} (conf={confidence})")
            return
    else:
        if not should_reply or confidence < ACTIVE_CONFIG["intent_confidence_threshold"]:
            logger.debug(f"[小爱] 群 {group_id} 意图判断不通过: {reason} (conf={confidence})")
            return

    logger.info(f"[小爱] 群 {group_id} 意图通过: {reason} (conf={confidence:.2f})")

    # 生成对话摘要
    summary = await summarize_conversation(msgs)
    logger.debug(f"[小爱] 对话摘要: {summary}")

    # 生成回复
    reply = await generate_reply_with_context(msgs, reason, summary)
    if not reply:
        return

    # 质量评分
    quality = await evaluate_reply_quality(reply, summary, msgs)
    if quality < ACTIVE_CONFIG["quality_threshold"]:
        logger.info(f"[小爱] 回复质量过低 ({quality:.2f})，放弃: {reply}")
        return

    # 语义重复检测
    if is_semantic_duplicate(reply, recent_replies):
        logger.info(f"[小爱] 回复语义重复，跳过: {reply}")
        return

    # 同一话题冷却
    current_topic = None
    for kw in GAME_KEYWORDS:
        if kw in reply:
            current_topic = kw
            break
    if current_topic and cache.get("last_topic") == current_topic:
        if now - cache["last_reply"] < ACTIVE_CONFIG["same_topic_cooldown"]:
            logger.info(f"[小爱] 同一话题[{current_topic}]短时间内重复，跳过")
            return

    # 发送（成功后才更新冷却计时，避免发送失败白白进入冷却）
    logger.info(f"[小爱] 决定回复: {reply} (质量={quality:.2f})")
    sent = await send_text_to_group(group_id, reply)
    if sent:
        cache["last_reply"] = time.time()
        cache["last_topic"] = current_topic if current_topic else ""
        recent_replies.append(reply)

# ==================== 主动回复后台任务 ====================
async def active_reply_loop():
    await asyncio.sleep(10)
    logger.info(f"[小爱] 智能后台任务 v4.2 已启动，每 {ACTIVE_CONFIG['check_interval']} 秒检查一次")

    while True:
        logger.debug("[小爱] 主动检查循环执行")
        await asyncio.sleep(ACTIVE_CONFIG["check_interval"])
        if not ACTIVE_CONFIG["enable"]:
            continue

        now = time.time()

        # 清理长期不活跃的群缓存，避免内存无限增长
        if len(group_cache) > 50:
            for gid in [gid for gid, c in group_cache.items() if now - c["last_active"] > GROUP_CACHE_EXPIRE]:
                group_cache.pop(gid, None)

        for group_id, cache in list(group_cache.items()):
            try:
                await _process_group(group_id, cache, now)
            except Exception as e:
                # 单个群处理失败不影响后台任务整体运行
                logger.error(f"[小爱] 处理群 {group_id} 时发生异常: {e}")

# ==================== 消息监听 ====================
@sv.on_message()
async def handle_message(bot: Bot, event: Event):
    # 兜底启动后台任务（模块导入时若无运行中的事件循环会延迟到这里启动）
    start_task_if_not()

    if event.user_type == "direct":
        return

    user_name = event.sender.get("nickname", "未知用户") if event.sender else "未知用户"
    add_to_cache(
        group_id=event.group_id,
        user_id=event.user_id,
        user_name=user_name,
        message=event.text.strip()
    )

    # 被@回复
    if event.is_tome:
        now = time.time()
        cache = group_cache.get(event.group_id)
        if cache and now - cache.get("last_at_reply", 0) < AT_REPLY_COOLDOWN:
            logger.debug(f"[小爱] 群 {event.group_id} 被@回复冷却中")
            return
        logger.info(f"[小爱] 群 {event.group_id} 收到@")
        msgs = list(cache["msgs"])[-10:] if cache else []
        reply = await generate_at_reply(msgs, event.text.strip(), user_name)
        if reply:
            logger.info(f"[小爱] 被@回复: {reply}")
            sent = await send_text_to_group(event.group_id, reply)
            if sent and cache:
                cache["last_at_reply"] = now
        else:
            logger.warning("[小爱] 被@回复生成失败")

# ==================== 启动任务 ====================
_task: Optional[asyncio.Task] = None


def start_task_if_not():
    """启动后台任务；若当前无运行中的事件循环（如模块被同步导入），则推迟到首条消息时再启动"""
    global _task
    if _task is not None and not _task.done():
        return
    try:
        _task = asyncio.create_task(active_reply_loop())
    except RuntimeError:
        _task = None
        return
    logger.info("[小爱] 后台任务已注册")


start_task_if_not()
