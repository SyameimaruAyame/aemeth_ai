<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/feixinxueron.png" width="120" alt="爱弥斯头像">
</p>

# 🌊 爱弥斯 AI 角色对话插件 (aemeth_ai)

🚧 支持 QQ 群/频道、OneBot、微信、KOOK、Tg、飞书、DoDo、米游社、Discord 的 Bot 插件
🚧 [安装文档](https://docs.sayu-bot.com/)

注意：该插件为早柚核心 (gsuid_core) 的扩展，具体安装方式可参考 [GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)

一个为 [gsuid-core](https://github.com/KimigaiiWuyi/gsuid-core) 设计的 AI 文字对话插件。  
让机器人以《鸣潮》角色「爱弥斯」的风格与群友互动，支持自定义角色、智能问答和联网搜索。

---

## ✨ 功能特点

- **🎭 角色自由定制**：只需修改系统提示词，即可让机器人扮演任何角色（爱弥斯、胡桃、守岸人，或你原创的角色）。
- **🧠 智能问答**：集成 DeepSeek 大模型，能回答游戏攻略、百科知识、闲聊互动。
- **🔍 联网搜索（可选）**：通过 Serper API 获取最新信息，回答攻略、实时资讯类问题。
- **📉 低频率高质量**：内置意图判断、概率闸口和质量过滤，只在有意义时发言，避免刷屏。
- **💰 低 token 消耗**：常规框架功能多但 API 消耗大，本插件在保证回复质量的同时，节省大量 token / API 调用成本。
- **🐳 Docker 友好**：所有配置均通过环境变量注入，无需修改代码即可容器化部署。
- **📦 即插即用**：复制到 gsuid-core 插件目录即可使用。

---

## 🗣️ 推荐联动：全局语音插件 (voice_reply)

推荐配合使用插件——[**全局语音插件**](https://github.com/SyameimaruAyame/voice_reply)。

*   **作用**：该插件会在本地查找与回复文本匹配的语音文件并发送，让机器人真正“发出声音”。
*   **搭配效果**：`aemeth_ai` 负责生成智能、有趣的文字回复，`voice_reply` 负责将回复“读”出来，两者结合能极大提升群内互动的真实感和趣味性。
*   **使用方式**：只需将 `voice_reply` 也放入 gsuid-core 的插件目录，它会自动工作。当 `aemeth_ai` 生成回复后，如果语音库中有对应的音频，就会优先发送语音。

---

## 📥 安装

1. **进入 gsuid-core 插件目录**
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

4. **重启 gsuid-core**

---

## 🔑 配置

插件使用 **DeepSeek** 大模型（OpenAI 兼容 HTTP 接口），主动发言通过 **OneBot v11 HTTP API** 发送，联网搜索为可选功能。
**所有配置均通过环境变量设置**（也可直接修改 `__init__.py` 配置区的默认值），请勿公开包含密钥的配置。

### 1. 获取 API Key

| 服务 | 用途 | 获取地址 |
| :--- | :--- | :--- |
| **DeepSeek** | 大模型对话（必需） | [platform.deepseek.com](https://platform.deepseek.com/) |
| **Serper** | 联网搜索（可选） | [serper.dev](https://serper.dev) |

### 2. 环境变量一览

| 环境变量 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（必需） | 无 |
| `DEEPSEEK_BASE_URL` | DeepSeek 接口地址，一般无需修改 | `https://api.deepseek.com` |
| `ONEBOT_API_URL` | OneBot v11 HTTP API 地址（必需可达） | `http://127.0.0.1:5700` |
| `ONEBOT_ACCESS_TOKEN` | OneBot 端配置的 access_token（没有则留空） | 无 |
| `SERPER_API_KEY` | Serper 搜索 Key（可选） | 无 |

仓库内附 `.env.example`，可复制为 `.env` 后按实际情况填写。

### 3. 关于 `ONEBOT_API_URL`（重要）

主动发言的后台任务不在消息事件上下文中，拿不到框架的 Bot 对象，因此插件通过 **OneBot v11 的 HTTP 接口**（`POST {ONEBOT_API_URL}/send_group_msg`）发送群消息。

- 该服务由你的协议端提供（go-cqhttp / NapCat / LLOneBot 等），**需要在协议端配置中启用 HTTP API**，并确认端口（go-cqhttp 默认为 `5700`，NapCat / LLOneBot 常见为 `3000`）。
- 如果协议端设置了 `access_token`，请同步配置 `ONEBOT_ACCESS_TOKEN`。

### 4. 🐳 Docker 部署说明

**容器内的 `127.0.0.1` 指向容器自身，不是宿主机**。gsuid-core 跑在 Docker 中时，默认值 `http://127.0.0.1:5700` 无法访问宿主机或其他容器上的 OneBot，请按组网方式修改：

| 组网方式 | `ONEBOT_API_URL` 示例 |
| :--- | :--- |
| OneBot 在宿主机（Linux 默认 bridge） | `http://172.17.0.1:5700` |
| OneBot 在宿主机（Docker Desktop / 配置了 host-gateway 的 Linux） | `http://host.docker.internal:5700` |
| OneBot 与 core 在同一 docker-compose 网络 | `http://<服务名>:<端口>`，如 `http://napcat:3000` |
| core 容器使用 `--network host`（Linux） | `http://127.0.0.1:5700` 保持默认即可 |

> Linux 下想用 `host.docker.internal`，需在启动容器时加 `--add-host=host.docker.internal:host-gateway`，或在 compose 中配置 `extra_hosts`。

docker-compose 环境变量示例：

```yaml
services:
  gsuid-core:
    environment:
      - DEEPSEEK_API_KEY=sk-xxxxxxxx
      - ONEBOT_API_URL=http://napcat:3000
      - ONEBOT_ACCESS_TOKEN=
      - SERPER_API_KEY=
```

### 5. 替换其他模型 / 接口

`call_llm` 走的是 OpenAI 兼容的 `POST {DEEPSEEK_BASE_URL}/chat/completions`。任何兼容该协议的网关（OpenAI、通义千问兼容模式、OneAPI 等）都可以直接用：

1. 将 `DEEPSEEK_BASE_URL` 改为目标网关地址（如阿里云兼容模式为 `https://dashscope.aliyuncs.com/compatible-mode/v1`）；
2. 将 `DEEPSEEK_API_KEY` 换成对应平台的 Key；
3. 修改 `__init__.py` 中 `MODELS` 字典里的模型名（如 `gpt-4o-mini`、`qwen-plus`）。

---

## 🎮 使用示例

**直接呼唤**  
在群里发送“小爱 鸣潮今汐怎么配队”，机器人会结合搜索回答。

**@机器人**  
@机器人并提问，会结合上下文回答（被@回复有 60 秒群冷却）。

**被动参与**  
当群聊热烈讨论游戏话题时，机器人有极低概率主动插话（见下方高级配置）。

<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/ai.png" width="600" alt="聊天示例">
</p>

---

## 🎨 自定义角色

插件默认扮演《鸣潮》的「爱弥斯」（自称小爱）。如需更换角色，只需修改 `__init__.py` 中 `generate_reply_with_context` 函数内的 `system_prompt` 变量。

**修改步骤**

1. 打开 `aemeth_ai/__init__.py`；
2. 搜索 `system_prompt`，找到爱弥斯设定那段长字符串；
3. 将其内容替换为你想要的角色设定（建议包含【核心设定】和【说话风格】两部分）；
4. 保存并重启 core 生效。

**示例：替换为胡桃（《原神》）**

```python
system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《原神》中的“胡桃”，自称“本堂主”。

【核心设定】
- 你是往生堂的第77代堂主，古灵精怪，喜欢搞怪和押韵。
- 你总是笑嘻嘻的，喜欢推销“优惠套餐”，但其实很关心身边的人。

【说话风格】
1. **俏皮话多，喜欢押韵**：每句话都想押韵，不行也没关系~
2. **自称“本堂主”**，偶尔冒出几句打油诗。
3. **语气活泼**，一句话不超过20字。"""
```

---

## ⚙️ 高级配置

在 `__init__.py` 文件开头的 `ACTIVE_CONFIG` 字典中可调整以下参数：

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `base_trigger_prob` | 通过关键词粗筛后的放行概率 (0~1)，调高显著变活跃 | 0.005 |
| `check_interval` | 后台检查间隔（秒） | 60 |
| `cooldown` | 主动发言冷却（秒） | 300 |
| `same_topic_cooldown` | 同一话题冷却（秒） | 600 |
| `silence_limit` | 冷场阈值（秒），超过则不检查 | 180 |
| `intent_confidence_threshold` | 意图判断置信度（越高越保守） | 0.8 |
| `quality_threshold` | 质量评分阈值（越高越严格） | 0.7 |
| `enable_intent_filter` | 是否启用意图判断 | `True` |
| `enable_quality_filter` | 是否启用质量过滤 | `True` |
| `enable_web_search` | 是否启用联网搜索 | `True` |

不建议无经验用户随意修改，调整前请先备份。

---

## ❓ 常见问题

**Q：为什么机器人不说话？**  
A：插件设有严格的质量门槛，只有当模型认为有高质量回复时才发言。你可适当降低 `intent_confidence_threshold` 和 `quality_threshold`，或调高 `base_trigger_prob` 来提高活跃度。同时检查日志中是否有 `无法连接 OneBot HTTP API` 的报错。

**Q：日志报“无法连接 OneBot HTTP API”？**  
A：说明协议端的 HTTP 服务不可达。检查：① 协议端（go-cqhttp / NapCat / LLOneBot）是否启用了 HTTP API；② 端口是否正确；③ 如果 core 跑在 Docker 里，`ONEBOT_API_URL` 不能是 `127.0.0.1`，请参考上方 Docker 部署说明。

**Q：如何让机器人更活跃？**  
A：调高 `base_trigger_prob`（如 0.05~0.2）并缩短 `cooldown`（如 60）。注意 token 消耗会同步上升。

**Q：不想用联网搜索怎么办？**  
A：不设置 `SERPER_API_KEY` 或将 `enable_web_search` 设为 `False`。

**Q：可以用 DeepSeek 之外的模型吗？**  
A：可以，参考“配置 → 替换其他模型 / 接口”一节，任何 OpenAI 兼容接口均可。

**Q：可以同时用多个角色吗？**  
A：一个插件实例只能固定一个角色。如需多角色，可复制插件文件夹，分别修改 `system_prompt` 并赋予不同 SV 名称。

---

## 📄 许可证

本项目采用 MIT 许可证。

## 💬 反馈与贡献

欢迎提交 Issues 或 Pull Requests
还在不断优化中，一起让这个小插件变得更好！
