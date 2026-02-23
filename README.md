<p align="center">
  <img src="[https://i0.hdslb.com/bfs/face/3e0e929e4b3d6f32c553e4a7f52f975bd9a2d939.jpg@128w_128h_1c_1s.webp]" width="120" alt="爱弥斯头像">
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
- **🔍 联网搜索（可选）**：通过 Serper API 获取最新信息，回答“今天天气”“金价多少”等实时问题。
- **📉 低频率高质量**：内置意图判断和质量过滤，只在有意义时发言，避免刷屏。
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

### 3. 替换其他 API 模型（进阶）
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

效果示例
群友A：小爱，牢忌现在强度如何？
小爱：牢忌（忌炎）现在还是t1水平呢，小爱看了最新攻略，他依然很能打哦~

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

## ❓ 常见问题
Q：为什么机器人不说话？
A：插件设有严格的质量门槛，只有当模型认为有高质量回复时才发言。你可适当降低 intent_confidence_threshold 和 quality_threshold 来提高活跃度。

Q：如何让机器人更活跃？
A：调高 base_trigger_prob（如 0.02）并缩短 cooldown（如 60）。

Q：不想用联网搜索怎么办？
A：不设置 SERPER_API_KEY 或将 enable_web_search 设为 false。

Q：可以同时用多个角色吗？
A：一个插件实例只能固定一个角色。如需多角色，可复制插件文件夹，分别修改 system_prompt 并赋予不同 SV 名称。

## 📄 许可证
本项目采用 MIT 许可证。

## 💬 反馈与贡献
欢迎提交 Issues 或 Pull Requests
还在不断优化中，一起让这个小插件变得更好！
