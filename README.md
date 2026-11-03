<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/feixinxueron.png" width="120" alt="爱弥斯头像">
</p>

<h1 align="center">🌊 爱弥斯 AI 角色对话插件 (aemeth_ai)</h1>

<p align="center">
  为 <a href="https://github.com/KimigaiiWuyi/gsuid-core">早柚核心 (gsuid_core)</a> 编写的 AI 群聊插件<br>
  让机器人以《鸣潮》角色「爱弥斯」的风格和群友聊天，自称「小爱」
</p>

---

## 📖 简介

`aemeth_ai` 是一个运行在早柚核心 (gsuid_core) 上的 AI 对话插件。它内置一条「先判断该不该说、再决定说什么」的决策链，只在真正有意义的时候开口，因此既能保证回复质量，也能把 token 消耗压到很低。

插件不绑定任何具体的 QQ 框架：消息发送直接复用 gsuid_core 当前已建立的 Bot 连接，所以 NapCat、LLOneBot、Lagrange、go-cqhttp 等 OneBot v11 实现都能直接使用，无需额外开放端口。

## ✨ 功能特点

- **🎭 角色自由定制**：角色设定集中在 `system_prompt` 里，改一段文本就能换成任何角色（胡桃、守岸人，或你原创的角色）。
- **💬 两种触发方式**：被 @ 或消息里出现「小爱」时即时回应；其余时间按概率评估是否主动插话。
- **🧠 结构化决策链**：关键词粗筛 → 意图判断 → 对话摘要 → 回复生成 → 质量评分 → 语义查重 → 冷却，逐层过滤掉低质量回复。
- **🔍 联网搜索（可选）**：接入 [Serper](https://serper.dev) API，遇到游戏 / 实时性话题时自动搜索后再作答。
- **📉 低 token 消耗**：廉价模型负责判断与评分，只在最后一步用生成模型出文本，比"每条消息都过一遍大模型"省得多。
- **🔌 零配置发送**：复用 gsuid_core 的 Bot 通道发送，WS 部署不需要任何额外端口，也不会出现选错 HTTP 端口的 404 问题。
- **📦 即插即用**：复制到插件目录即可加载，依赖只有一个 `aiohttp`。

---

## 📥 安装

1. **进入早柚核心的插件目录**

   ```bash
   cd /path/to/gsuid_core/gsuid_core/plugins
   ```

2. **克隆本插件**

   ```bash
   git clone https://github.com/SyameimaruAyame/aemeth_ai.git
   ```

3. **安装依赖**

   ```bash
   pip install -r aemeth_ai/requirements.txt
   ```

4. **重启早柚核心**，插件会被自动加载。

> 不知道该用哪个 Python 环境时，用早柚核心自己的虚拟环境（Windows 一般是 `gsuid_core\.venv\Scripts\pip.exe`）安装，避免装到别的解释器里。

## 🔑 配置

插件使用 **DeepSeek** 大模型（OpenAI 兼容接口，通过 `aiohttp` 直接请求），并支持可选的联网搜索。所有配置都优先读取环境变量，也可以直接改代码里的默认值——**不要把带 Key 的代码提交到公开仓库**。

### 1. 获取 API Key

| 服务 | 用途 | 获取地址 |
| :--- | :--- | :--- |
| **DeepSeek** | 大模型对话（必需） | [platform.deepseek.com](https://platform.deepseek.com/) |
| **Serper** | 联网搜索（可选） | [serper.dev](https://serper.dev) |

### 2. 填写 Key

**方式一：环境变量（推荐，Docker 部署尤其方便）**

```bash
export DEEPSEEK_API_KEY="sk-你的DeepSeek密钥"
export SERPER_API_KEY="你的Serper密钥"        # 可选，不填则关闭联网搜索
```

**方式二：直接改代码**

打开 `aemeth_ai/__init__.py`，找到文件开头的配置区：

```python
# 不想用环境变量，就把第二个参数换成你的 Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")     # 可选
```

### 3. 消息发送（重要）

**默认不需要任何配置。**

插件的发送逻辑优先复用 **gsuid_core 已经连上的 Bot 通道**——也就是你的 NapCat / LLOneBot 连过来的那条 WebSocket。消息会沿着同一条连接回传，因此：

- 不需要再单独开一个 HTTP 端口；
- 不管你的框架用的是正向 WS 还是反向 WS，都能正常发出；
- 不会出现「日志显示回复生成成功，但群里没有消息」的情况。

只有下面这种特殊情况才需要配置 HTTP 兜底：你想让插件完全绕过框架、直接调用 OneBot HTTP 接口。此时设置环境变量：

```bash
export ONEBOT_API_URL="http://127.0.0.1:3000"   # 换成你自己的 OneBot HTTP 端口
```

留空（默认）即关闭 HTTP 发送。需要注意各框架的 HTTP 端口并不相同：

| 框架 | 常见 HTTP 端口 | 备注 |
| :--- | :--- | :--- |
| NapCat | `3000` | 需在「网络配置 → HTTP 服务器」里手动开启 |
| go-cqhttp | `5700` | 配置文件里的 `servers.http` |
| LLOneBot | `3000` | 与 NapCat 类似 |

> **遇到 `HTTP 404: not found` 就是配错了端口。** 404 说明那个地址上确实有服务在监听，但它不是 OneBot 的 HTTP 接口（比如 8080 常被各种 Web 面板占用）。不用 HTTP 的话，把 `ONEBOT_API_URL` 删掉即可。

### 4. 换成其他大模型

只要对方兼容 OpenAI 的 `chat/completions` 接口，改两行就能用：

1. 改模型名：`__init__.py` 里的 `MODELS` 字典，`"cheap"` 用于判断与评分，`"smart"` 用于生成回复（默认两者都是 `deepseek-chat`，想压成本可以改成更小的模型）。
2. 改接口地址：把 `DEEPSEEK_BASE_URL` 换成目标服务的地址，例如通义千问为 `https://dashscope.aliyuncs.com/compatible-mode/v1`，同时替换 API Key。

## 🎮 使用示例

**@ 机器人**

> @小爱 今汐的声骸怎么配？
>
> 小爱：今汐主 C 的话，双爆伤加共鸣效率会更稳哦~

**直接呼叫**

> 小爱今天天气怎么样
>
> 小爱：小爱看不到窗外呢，不过搜到说今天多云转晴，记得带件外套~

**被动参与**

群聊连续讨论游戏话题时，插件会按 `base_trigger_prob`（默认 0.5%）的概率抽样，再经意图判断和质量评分，都通过才会插话，所以不会刷屏。

<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/ai.png" width="600" alt="聊天示例">
</p>

## 🎨 自定义角色

插件默认扮演《鸣潮》的「爱弥斯」。想换角色，只需要替换 `__init__.py` 中的 `system_prompt` 变量：

1. 打开 `aemeth_ai/__init__.py`；
2. 找到 `generate_reply_with_context()` 里的 `system_prompt = """..."""`；
3. 把里面的内容换成你想要的设定。建议保留【核心设定】和【说话风格】两段结构，模型更容易抓住重点；
4. 保存并重启早柚核心。

示例（换成《原神》的胡桃）：

```python
system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《原神》中的"胡桃"，自称"本堂主"。

【核心设定】
- 你是往生堂的第77代堂主，古灵精怪，喜欢搞怪和押韵。
- 你总是笑嘻嘻的，喜欢推销"优惠套餐"，但其实很关心身边的人。

【说话风格】
1. **俏皮话多，喜欢押韵**：每句话都想押韵，不行也没关系~
2. **自称"本堂主"**，偶尔冒出几句打油诗。
3. **语气活泼**，一句话不超过20字。"""
```

> 别忘了同时改 `generate_at_reply()` 里那句简短的 `system_prompt`，否则被 @ 时的回复风格会不统一。

## ⚙️ 配置项

以下参数都在 `__init__.py` 开头，按需调整即可，改完重启生效。

### 主动发言（`ACTIVE_CONFIG`）

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `enable` | 主动模式总开关，`false` 时只保留 @ 回复 | `true` |
| `check_interval` | 后台检查间隔（秒） | `60` |
| `base_trigger_prob` | 普通话题的插话概率（0~1） | `0.005` |
| `min_messages` | 非快速响应时，至少积累多少条消息才评估 | `3` |
| `cooldown` | 同群两次主动发言的最短间隔（秒） | `300` |
| `same_topic_cooldown` | 同一话题重复发言的冷却（秒） | `600` |
| `silence_limit` | 群聊静默超过该秒数就不再主动发言 | `180` |
| `max_cache` | 每个群缓存的最近消息条数 | `30` |
| `intent_confidence_threshold` | 意图判断置信度门槛，越高越保守 | `0.8` |
| `quality_threshold` | 回复质量评分门槛，越高越严格 | `0.7` |
| `enable_intent_filter` | 是否启用意图判断 | `true` |
| `enable_quality_filter` | 是否启用质量评分 | `true` |
| `enable_web_search` | 是否启用联网搜索 | `true` |
| `question_keywords` | 粗筛阶段的问题类关键词列表 | 见代码 |

### 其他常量

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `AT_REPLY_COOLDOWN` | 同群被 @ 回复的冷却（秒） | `10` |
| `MODELS["cheap"]` | 意图判断 / 摘要 / 评分使用的模型 | `deepseek-chat` |
| `MODELS["smart"]` | 回复生成使用的模型 | `deepseek-chat` |
| `GAME_KEYWORDS` | 游戏话题关键词，命中后走快速响应通道 | 见代码 |

代码里还有几个写死的阈值：快速响应通道的意图门槛为 `0.6`，语义查重的相似度阈值为 `0.65`。

> `ACTIVE_CONFIG` 里的 `min_messages_for_topic` 和模块级的 `SEARCH_KEYWORDS` 目前是预留字段，尚未参与逻辑，可以暂时忽略。

## 🧩 工作流程

```
群消息 ──► 写入缓存 + 记录当前 Bot
              │
              ├─ 是 @ ──► 立即生成回复 ──► 发送（Bot 通道）
              │
              └─ 后台每 60s 扫描
                    ├─ 冷却 / 静默 / 消息数 检查
                    ├─ 关键词粗筛 ──► 概率抽样
                    ├─ 意图判断（cheap 模型，JSON）
                    ├─ 生成对话摘要（cheap 模型）
                    ├─ 生成回复（smart 模型，可带搜索结果）
                    ├─ 质量评分 ──► 低于阈值则放弃
                    ├─ 语义查重 / 同话题冷却
                    └─ 发送（Bot 通道）
```

## 🛠 常见问题

**Q：机器人为什么一直不说话？**

A：这是设计如此。主动发言要依次通过概率抽样、意图判断（≥0.8）、质量评分（≥0.7）三道关卡，任何一道不过都不会开口。想更活跃可以调高 `base_trigger_prob`（比如 `0.02`）、降低 `intent_confidence_threshold`（比如 `0.6`）和 `quality_threshold`（比如 `0.6`）。另外，被 @ 会走即时回复通道（同群 10 秒冷却），可以先用它确认插件是否正常工作。

**Q：日志里明明生成了回复，群里却没收到？**

A：按顺序排查：

1. 日志里是否出现「已向群 xxx 发送文字」——出现说明已交给 Bot 通道，问题在 QQ 侧（例如被风控、账号掉线）；
2. 是否出现了「没有可用的 Bot 连接」——说明这个群还没收到过消息，Bot 实例没被记录，等群里有新消息后重试；
3. 是否出现 `HTTP 404` 或 `HTTP 发送失败`——说明你设了 `ONEBOT_API_URL` 但端口填错了，把它删掉就能回到默认的 Bot 通道。

**Q：不想用联网搜索怎么办？**

A：不设置 `SERPER_API_KEY`，或者把 `enable_web_search` 改成 `false`。

**Q：可以同时挂多个角色吗？**

A：一个插件实例只固定一个角色。需要多角色时，复制一份插件目录，改掉 `SV("...")` 里的名字和 `system_prompt` 即可。

**Q：被 @ 了但回复里全是客套话？**

A：`generate_at_reply()` 用的是精简版提示词，只保留一句话的风格约束；如果希望它也带上完整人设，可以把 `system_prompt` 抽成模块级常量给两个函数共用。

## 🚧 Roadmap

以下功能在早期文档里提到过，但当前代码**尚未实现**，欢迎 PR：

- [ ] 表情包：按情绪发送本地图片
- [ ] 自由模式 / 召唤模式的主人指令切换
- [ ] 场景感知与话题分段摘要
- [ ] 回复走语音合成 / 音频文件

## 📄 许可证

本项目采用 MIT 许可证。

## 💬 反馈与贡献

欢迎提交 Issue 或 Pull Request。提交前建议先跑一遍 `python -m py_compile aemeth_ai/__init__.py` 确认语法没问题。
