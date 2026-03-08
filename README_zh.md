# Browser-Use 交互式 CLI 应用程序

[English](./README.md) | [中文](./README_zh.md) | [Español](./README_es.md)

> **🤖 AI 开发项目**：此项目完全由 AI 开发，经过数十轮优化，所有 bug 最终由 **Gemini 3.1 Pro** 解决，确保功能完善。

一个基于 browser-use 库构建的交互式浏览器控制应用程序。使用自然语言命令控制浏览器自动化。

## 功能特性

- **自然语言控制**：使用纯英文描述任务，例如 "open google"、"close cookie popup"、"search for Python tutorials"
- **持久化浏览器会话**：浏览器在命令之间保持打开状态，支持多步骤工作流
- **可视化模式**：浏览器窗口可见，您可以实时观察自动化过程
- **REPL 界面**：支持历史记录的连续命令循环
- **强大的错误处理**：即使个别命令失败，应用程序仍继续运行
- **优雅退出**：使用 Ctrl+C 或 exit/quit 命令正常退出
- **多 LLM 支持**：支持 OpenAI、Gemini、NVIDIA 或任何 OpenAI 兼容的 API
- **多模型自动回退**：在 .env 中配置多个模型；如果一个失败，自动切换到下一个
- **浏览器立即启动**：浏览器在启动时打开并等待命令

## 环境要求

- Python 3.10+
- LLM API 访问权限（OpenAI 或兼容服务）

## 安装步骤

1. 克隆或下载项目文件

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置 `.env` 文件：
```env
# LLM API 配置
OPENAI_API_KEY=your_api_key_here

# 可选：自定义 API Base URL（默认：https://api.openai.com/v1）
OPENAI_API_BASE=https://api.openai.com/v1

# 可选：模型名称（支持多个模型，用逗号分隔）
# 如果指定了多个模型，系统将在一个失败时自动尝试下一个
# 示例：MODEL_NAME=qwen/qwen3.5-122b-a10b,deepseek-chat,gpt-4o
MODEL_NAME=gpt-4o
```

**注意**：您可以使用任何 OpenAI 兼容的服务：
- NVIDIA：`OPENAI_API_BASE=https://integrate.api.nvidia.com/v1`
- Google Gemini：`OPENAI_API_BASE=https://generativelanguage.googleapis.com/v1beta/openai`
- DeepSeek：`OPENAI_API_BASE=https://api.deepseek.com/v1`
- 本地模型（Ollama、LM Studio）：`OPENAI_API_BASE=http://localhost:11434/v1`

## 使用方法

运行应用程序：
```bash
python main.py
```

浏览器将自动启动，您将看到命令提示符。浏览器窗口将打开并等待您的命令。

### 命令行选项

```bash
python main.py [-h] [-m {dom,screen}] [-c COMMAND]

# 选项：
#   -h, --help            显示帮助信息
#   -m, --mode {dom,screen}
#                         操作模式：'dom'（仅文本）或 'screen'（带截图/视觉）
#                         默认值：screen
#   -c, --command COMMAND
#                         执行单个命令并退出
```

### 示例

```bash
# 交互模式（默认）
python main.py

# 单命令模式
python main.py -c "打开谷歌并搜索 Python"

# 使用 DOM 模式（仅文本，无截图）
python main.py -m dom

# 单命令模式 + DOM 模式
python main.py -m dom -c "当前页面标题是什么？"
```

### 示例命令

```
Command > go to google.com
Command > accept the cookie consent
Command > search for browser-use python library
Command > click the first result
Command > what is the current page title?
Command > go to bing.com
Command > exit
```

### 特殊命令

- `help` - 显示帮助信息
- `status` - 显示浏览器状态
- `exit` / `quit` - 退出程序
- `Ctrl+C` - 强制退出

## 工作原理

1. 应用程序启动并初始化浏览器（可视化模式）和 LLM 配置
2. 使用 browser-use 的 Agent 来解释和执行自然语言命令
3. Agent 分析页面 DOM 并决定要执行的操作（点击、输入、导航等）
4. 浏览器会话在命令之间保持持久化 - Agent 记住之前的上下文
5. 每个命令都被添加到 Agent 的任务列表中并按顺序执行

## 项目结构

```
.
├── main.py # 主应用程序入口
├── requirements.txt # 依赖项
├── .env # 配置文件（需要创建）
├── README.md # 英文文档
├── README_zh.md # 中文文档
├── README_es.md # 西班牙语文档
└── test_*.py # 测试文件（可选）
```

## 故障排除

1. **API 密钥错误**：确保 `.env` 文件存在且 `OPENAI_API_KEY` 设置正确
2. **浏览器启动失败**：检查是否有其他浏览器实例正在运行，或尝试重新启动
3. **命令失败**：某些复杂页面可能需要更详细的命令；LLM 会尝试解释
4. **导入错误**：确保已使用 `pip install -r requirements.txt` 安装依赖
5. **Windows 上的 Unicode 错误**：应用程序自动配置 UTF-8 编码
6. **LLM JSON 解析错误**：应用程序现在包含备用 LLM 并禁用思考模式，以提高与某些模型的兼容性
7. **浏览器状态未持久化**：应用程序现在使用 `user_data_dir` 将 cookies、登录会话和其他浏览器状态持久化在 `browser_data/` 目录中

## 技术细节

- **browser-use 版本**：0.12.1
- **架构**：单个持久化 Agent 实例，使用 `keep_alive=True` 的浏览器配置文件
- **多任务支持**：使用 `agent.add_new_task()` 排队命令，而无需重置浏览器状态
- **异步/等待**：完整的异步实现，提供响应灵敏的 CLI
- **浏览器数据持久化**：使用 `user_data_dir` 将浏览器配置文件存储在 `browser_data/` 目录中，保留 cookies、登录会话和其他浏览器状态

## 注意事项

- 首次运行会下载浏览器驱动（Playwright）- 这可能需要一些时间
- 建议使用可视化模式（`headless=False`）进行调试
- 某些网站有反机器人措施 - 请负责任地使用并遵守服务条款
- 最好在测试环境中使用；避免自动化生产网站

## 简单测试及模型表现

### 测试命令

```bash
python main.py -c "第一步、打开这个网页（番茄小说的小说管理界面）：https://fanqienovel.com/main/writer/chapter-manage/7601645527918201918&共和国特工?type=1 。第二步、根据网页内容判断上一次发布的最新章节序号，不需要翻页，默认显示的就是一定是最新章节。计算出你要发布的新一章序号（例如上一章是130，新章节就是131）。新一章对应的本地文件路径是：C:\Code\iNovel-v2.3\data\chapters\chapter-[序号].txt （注意替换实际的新章节序号，严禁修改目录结构，如果使用工具读取时报错找不到文件就停止操作，结束流程）。第三步、点击新建章节。第四步、在章节新建页面的填入工作，规则如下：【章节序号】计算出的新章节纯数字序号填到第___章之间的那个框（第一个可输入文本框）；【标题】请使用 read_local_file 工具，设置 start_line=1, end_line=1 读取第一行内容。你需要智能提取标题部分（去除"标题：""《""》"等字样），然后填入标题框(提示："请输入标题..."，第二个可输入文本框)；【正文】请直接使用 fill_from_file 动作，指定 index 为正文编辑框（提示"请输入正文..."的那个大文本框，第三个可输入文本框）的序号，设置 file_path 为刚才的文件路径，并且设置 start_line=3（从第二行开始读取全部正文），让系统直接填充，不要尝试自己复制粘贴正文内容。第五步、填入完毕后点击下一步。后续步骤处理弹窗：弹窗类型一、问有错别字未修改，不用理会，点击提交继续。弹窗类型二、问是否进行内容风险监测，点击确定。弹窗类型三、发布设置窗口，在是否使用AI的部分选择"否"(右边那个radiobox)，不要点击确认发布，然后暂停100秒后，退出。弹窗类型四、内容检测不合格，就退出流程，停止操作。弹窗类型五、提示本地服务器版本冲突什么，不用理会。"
```

> **注意**：该测试只有支持图片输入的大模型才能正常工作，否则必然失败。

### 模型测试结果

| 模型 | 结果 | 时间 |
|------|------|------|
| Gemini 2.5 Flash-lite | ✅ 合格（中间有一个错误修复） | 快：1:30 |
| Gemini 2.5 Flash | 🟢 良好 | 快：1:30 |
| Gemini 3.0 Flash | 🟢 良好 | 快：1:30 |
| Gemini 3.1 Flash Lite | 🟢 良好 | 快：1:15 |
| *** 以下模型由 ModelScope 提供 *** | | |
| Xiaomi MIMO V2 Flash | 🟢 良好 | 慢：3:15 |
| K2.5 | ✅ 合格（有非致命错误） | 中等：2:13 |
| Qwen3.5 35B | ⚠️ 勉强（最后一步错误） | 快：1:12 |
| Qwen3.5 27B | 🟢 良好 | 中等：2:35 |
| Qwen3.5 122B | ✅ 合格（中间错误修复） | 快：1:25 |
| Qwen3.5 397B | ⚠️ 勉强（最后一步错误） | 快：1:20 |

## 许可证

MIT License