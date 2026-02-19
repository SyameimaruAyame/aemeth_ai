# 🌊 爱弥斯 AI 角色对话插件 (aemeth_ai)

🚧支持QQ群/频道、OneBot、微信、KOOK、Tg、飞书、DoDo、米游社、Discord的股票Bot插件
🚧[安装文档](https://docs.sayu-bot.com/)
丨安装提醒
注意：该插件为早柚核心(gsuid_core)的扩展，具体安装方式可参考[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)

支持NoneBot2 & HoshinoBot & ZeroBot & YunzaiBot & Koishi的AI 角色对话插件)

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

##🔑 配置

插件需要两个 API Key（均提供免费额度），请通过环境变量设置，切勿直接修改代码。

环境变量	说明	获取地址

DASHSCOPE_API_KEY	阿里云 DashScope API Key（用于大模型）	阿里云百炼

SERPER_API_KEY	Serper API Key（用于联网搜索，可选）	serper.dev

##设置环境变量示例（Linux/macOS）
   export DASHSCOPE_API_KEY="你的key"
   export SERPER_API_KEY="你的key"   # 若不设置，则禁用联网搜索

如果使用 systemd 或 Docker，请参照相应方式配置环境变量。

##🎮 使用示例
直接呼唤
在群里发送“小爱今天天气怎么样”，机器人会自动搜索并回答。

@机器人
@机器人并提问，会结合上下文回答。

被动参与
当群聊热烈讨论游戏话题时，机器人有极低概率主动插话（可在配置中调整）。

效果示例
群友A：小爱，牢忌现在强度如何？
小爱：牢忌（忌炎）现在还是t1水平呢，小爱看了最新攻略，他依然很能打哦~

🎨 自定义角色
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

##⚙️ 高级配置
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

##❓ 常见问题
Q：为什么机器人不说话？
A：插件设有严格的质量门槛，只有当模型认为有高质量回复时才发言。你可适当降低 intent_confidence_threshold 和 quality_threshold 来提高活跃度。

Q：如何让机器人更活跃？
A：调高 base_trigger_prob（如 0.02）并缩短 cooldown（如 60）。

Q：不想用联网搜索怎么办？
A：不设置 SERPER_API_KEY 或将 enable_web_search 设为 false。

Q：可以同时用多个角色吗？
A：一个插件实例只能固定一个角色。如需多角色，可复制插件文件夹，分别修改 system_prompt 并赋予不同 SV 名称。

##📄 许可证
本项目采用 MIT 许可证。

##💬 反馈与贡献
欢迎提交 Issues 或 Pull Requests
一起让这个小插件变得更好！