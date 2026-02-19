AI 角色对话插件 (gsuid-core)
一个为 gsuid-core 设计的 AI 文字对话插件，支持自由更换角色性格，并可选联网搜索实时信息。

✨ 功能特点
🎭 角色自由定制：只需修改系统提示词，即可让机器人扮演任何角色（爱弥斯、胡桃、守岸人，或你原创的角色）。

🧠 智能问答：集成大语言模型，能回答游戏攻略、百科知识、闲聊互动。

🔍 联网搜索（可选）：通过 Serper API 获取最新信息，回答实时问题（天气、金价等）。

📉 低频率高质量：内置意图判断和质量过滤，只在有意义时发言，避免刷屏。

📦 即插即用：复制到 gsuid-core 插件目录即可使用。

📦 安装
bash
# 进入 gsuid-core 插件目录
cd /path/to/gsuid_core/gsuid_core/plugins

# 克隆本插件
git clone https://github.com/你的用户名/gsuid-plugin-ai-chat.git ai_chat

# 安装依赖
pip install -r ai_chat/requirements.txt

# 重启 gsuid-core
🔑 快速配置
插件需要两个 API Key（均有免费额度）：

阿里云 DashScope：用于调用大模型（申请地址）

Serper：用于联网搜索，可选（申请地址）

建议通过环境变量设置：

bash
export DASHSCOPE_API_KEY="你的key"
export SERPER_API_KEY="你的key"   # 不设置则无法搜索
如不方便使用环境变量，也可直接修改 __init__.py 开头的对应变量。

🎨 自定义角色
打开 ai_chat/__init__.py，找到 system_prompt 变量（约 200 行），修改其中的设定即可改变机器人性格。

当前默认角色：爱弥斯（《鸣潮》）

python
system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《鸣潮》中的“爱弥斯”，自称“小爱”……"""
换成胡桃示例：

python
system_prompt = """你是一个活跃在QQ群的AI助手，你的角色是《原神》中的“胡桃”，自称“本堂主”……"""
更多角色示例可参考 character_examples.md（可自行创建）。

💬 使用示例
直接呼唤：在群里发送“小爱今天天气怎么样”，机器人会自动搜索并回答。

@机器人：@机器人并提问，会结合上下文回答。

被动参与：当群聊热烈讨论游戏话题时，机器人有极低概率主动插话（可关闭）。

❓ 常见问题
Q：为什么机器人不说话？
A：插件设有严格的质量门槛，只有当模型认为有高质量回复时才发言。可通过调整 __init__.py 中的 ACTIVE_CONFIG 参数改变活跃度（如降低 intent_confidence_threshold）。

Q：如何让机器人更活跃？
A：调高 base_trigger_prob（如 0.02）并缩短 cooldown（如 60）。

Q：不想用联网搜索怎么办？
A：不设置 SERPER_API_KEY 或将 enable_web_search 设为 false。

Q：可以同时用多个角色吗？
A：一个插件实例只能固定一个角色。如需多角色，可复制插件文件夹，分别修改 system_prompt 并赋予不同 SV 名称。