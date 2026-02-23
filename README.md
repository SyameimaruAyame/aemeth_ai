<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/feixinxueron.png" width="120" alt="爱弥斯头像">
</p>

# 🌊 爱弥斯 AI 角色对话插件 (aemeth_ai)

🚧 支持 QQ 群/频道、OneBot、微信、KOOK、Tg、飞书、DoDo、米游社、Discord 的 Bot 插件
🚧 [安装文档](https://docs.sayu-bot.com/)
丨安装提醒
注意：该插件为早柚核心 (gsuid_core) 的扩展，具体安装方式可参考 [GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)

支持 NoneBot2 & HoshinoBot & ZeroBot & YunzaiBot & Koishi 的 AI 角色对话插件

一个为 [gsuid-core](https://github.com/KimigaiiWuyi/gsuid-core) 设计的 AI 文字对话插件。  
让机器人以《鸣潮》角色「爱弥斯」的风格与群友互动，支持自定义角色、智能问答和联网搜索。

---

## ✨ 功能特点

- **🎭 角色自由定制**：只需修改系统提示词，即可让机器人扮演任何角色（爱弥斯、胡桃、守岸人，或你原创的角色）。
- **🧠 智能问答**：集成大语言模型，能回答游戏攻略、百科知识、闲聊互动。
- **😄 情绪表情包**：根据对话氛围实时分析小爱的情绪（开心/难过/惊讶等），并按设定概率发送对应情绪的表情包，让互动更生动。
- **🔍 联网搜索（可选）**：通过 Serper API 获取最新信息，回答“今天天气”“金价多少”等实时问题。
- **📉 低频率高质量**：内置意图判断和质量过滤，只在有意义时发言，避免刷屏。
- **📦 即插即用**：复制到 gsuid-core 插件目录即可使用。
- **📦 低sk消耗**：常规框架功能多但API消耗大，采用此插件能保证一定回复质量的同时，节省大量token/API调用成本。

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

2. **克隆本插件**
   ```bash
   git clone https://github.com/SyameimaruAyame/aemeth_ai.git

2. **安装依赖**
   ```bash
   pip install -r aemeth_ai/requirements.txt

重启 gsuid-core

## 🔑 配置

插件使用 **DeepSeek** 大模型（通过 OpenAI SDK 调用），并支持可选的联网搜索功能。**所有 API Key 均需直接在插件代码中填写**，请勿分享包含密钥的代码。

### 1. 获取 API Key

| 服务 | 用途 | 获取地址 |
| :--- | :--- | :--- |
| **DeepSeek** | 大模型对话（必需） | [platform.deepseek.com](https://platform.deepseek.com/) |
| **Serper** | 联网搜索（可选） | [serper.dev](https://serper.dev) |

### 2. 在插件中填写 Key

1. 打开插件文件 `aemeth_ai/__init__.py`。
2. 找到文件开头附近的**配置区**，你会看到如下代码：

   ```python
   # DeepSeek API 配置（直接填入你的 Key）
   DEEPSEEK_API_KEY = "你的DeepSeek API密钥"  # 替换为你的实际 Key
   deepseek_client = openai.OpenAI(
       api_key=DEEPSEEK_API_KEY,
       base_url="https://api.deepseek.com/v1"
   )

   # Serper API Key（可选，如果需要联网搜索就填）
   SERPER_API_KEY = "你的Serper API密钥"  # 替换为你的实际 Key，不需要则留空

### 3. 替换其他 API 模型
如果你希望使用其他模型（如 OpenAI 的 GPT、阿里云的通义千问等），可按以下方式修改：

修改模型名称：在 __init__.py 中找到 MODELS 字典，将 "cheap" 和 "smart" 对应的值改为目标模型（例如 "gpt-4o-mini"、"qwen-plus"）。

调整客户端配置：目前 deepseek_client 基于 OpenAI SDK 实现。如果其他 API 兼容 OpenAI SDK，只需修改 base_url 和 api_key 即可；若不兼容，则需要重写 call_llm 函数中的调用逻辑。

## 🎮 使用示例
直接呼唤
在群里发送“小爱今天天气怎么样”，机器人会自动搜索并回答。

@机器人
@机器人并提问，会结合上下文回答。

被动参与
当群聊热烈讨论游戏话题时，机器人有极低概率主动插话（可在配置中调整）。
<p align="center">
  <img src="https://raw.githubusercontent.com/SyameimaruAyame/images/main/ai.png" width="600" alt="聊天示例">
</p>

## 🎨 自定义角色
插件默认扮演《鸣潮》的「爱弥斯」（自称小爱）。如果你想更换角色，只需修改 __init__.py 中的 system_prompt 变量。

修改步骤
打开 aemeth_ai/__init__.py。

找到约第 200 行的 system_prompt 定义。

将其内容替换为你想要的角色设定（建议包含【核心设定】和【说话风格】）。

示例：替换为胡桃（《原神》）
python
system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《原神》中的“胡桃”，自称“本堂主”。

【核心设定】
- 你是往生堂的第77代堂主，古灵精怪，喜欢搞怪和押韵。
- 你总是笑嘻嘻的，喜欢推销“优惠套餐”，但其实很关心身边的人。

【说话风格】
1. **俏皮话多，喜欢押韵**：每句话都想押韵，不行也没关系~
2. **自称“本堂主”**，偶尔冒出几句打油诗。
3. **语气活泼**，一句话不超过20字。"""
修改后保存文件并重启 core 即可生效。

## ⚙️ 高级配置
在 __init__.py 中可以调整以下参数（位于文件开头的 ACTIVE_CONFIG 字典中）：

参数	说明	默认值

base_trigger_prob	主动发言概率 (0~1)	0.005

cooldown	主动发言冷却（秒）	300

intent_confidence_threshold	意图判断置信度（越高越保守）	0.8

quality_threshold	质量评分阈值（越高越严格）	0.7

enable_intent_filter	是否启用意图判断	true

enable_quality_filter	是否启用质量过滤	true

enable_web_search	是否启用联网搜索	true

不建议无经验用户随意修改，调整前请先备份。

## ⚙️ 高级配置

在 `__init__.py` 中可以调整以下参数（位于文件开头的 `ACTIVE_CONFIG` 字典及附近）：

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `base_trigger_prob` | 主动发言概率 (0~1) | 0.005 |
| `cooldown` | 主动发言冷却（秒） | 300 |
| `intent_confidence_threshold` | 意图判断置信度（越高越保守） | 0.8 |
| `quality_threshold` | 质量评分阈值（越高越严格） | 0.7 |
| `enable_intent_filter` | 是否启用意图判断 | `true` |
| `enable_quality_filter` | 是否启用质量过滤 | `true` |
| `enable_web_search` | 是否启用联网搜索 | `true` |

### 🔄 双模式切换

插件内置两种交互模式，可通过主人指令切换：

| 模式 | 行为 | 切换指令 |
| :--- | :--- | :--- |
| **自由模式** | 主动分析群聊话题，在合适时介入回复 | `小爱自由模式` |
| **召唤模式** | 仅在被@或消息包含“小爱”时回复 | `小爱召唤模式` |

> ⚠️ 模式切换指令仅限主人（在代码中配置的 `MASTER_QQ`）使用，其他用户发送指令会被忽略。

### 😄 表情包功能配置

表情包功能由以下两个参数控制：

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `ENABLE_EMOJI` | 是否启用表情包功能 | `true` |
| `EMOJI_PROB` | 每次回复后发送表情包的概率 (0~1) | `0.5` |

**表情包存放路径**：  
在插件目录下创建 `resources/emoji/` 文件夹，并根据情绪名称创建子文件夹（如 `happy`、`sad`、`angry`、`surprised`、`confused`、`neutral`）。将对应情绪的表情包图片放入相应文件夹（支持常见图片格式）。每次发送表情包时，会从对应情绪文件夹中随机选择一张图片发送。

**情绪自动判断**：  
插件会根据对话内容实时分析当前情绪，并用于选择表情包。情绪包括：`happy`、`sad`、`angry`、`surprised`、`confused`、`neutral`。若某情绪文件夹为空或无该文件夹，则不会发送表情包。

> 建议每个情绪文件夹至少放入3-5张图片，以增加随机性和趣味性。

### 📚 其他高级特性

- **场景感知**：自动识别对话场景（游戏讨论、日常闲聊、求助等），调整回复语气。
- **防抖**：短时间内的相似消息不重复处理。
- **对话分段**：自动检测话题转折，生成段落摘要，帮助理解长对话。
- **智能前缀**：1小时以上未互动才加“小爱在呢～”，否则直接回复。

## ❓ 常见问题

**Q：为什么机器人不说话？**  
A：插件设有严格的质量门槛，只有当模型认为有高质量回复时才发言。你可适当降低 `intent_confidence_threshold` 和 `quality_threshold` 来提高活跃度。

**Q：如何让机器人更活跃？**  
A：调高 `base_trigger_prob`（如 0.02）并缩短 `cooldown`（如 60），或切换到自由模式。

**Q：如何切换自由/召唤模式？**  
A：主人可在群内发送 `小爱自由模式` 或 `小爱召唤模式` 指令进行切换。切换后小爱会回复确认消息。

**Q：不想用联网搜索怎么办？**  
A：不设置 `SERPER_API_KEY` 或将 `enable_web_search` 设为 `false`。

**Q：表情包不发送怎么办？**  
A：检查 `ENABLE_EMOJI` 是否为 `true`，并确认对应情绪文件夹内存在图片文件。可在日志中搜索“情绪”查看当前情绪值。

**Q：可以同时用多个角色吗？**  
A：一个插件实例只能固定一个角色。如需多角色，可复制插件文件夹，分别修改 `system_prompt` 并赋予不同 SV 名称。

## 📄 许可证
本项目采用 MIT 许可证。

## 💬 反馈与贡献
欢迎提交 Issues 或 Pull Requests
还在不断优化中，一起让这个小插件变得更好！
