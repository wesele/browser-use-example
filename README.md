# Browser-Use Interactive CLI Application

[English](./README.md) | [中文](./README_zh.md) | [Español](./README_es.md)

> **🤖 AI-Developed Project**: This project was entirely developed by AI,经过数十轮优化, and all bugs were finally resolved by **Gemini 3.1 Pro** to ensure excellent functionality.

An interactive browser control application built on the browser-use library. Control browser automation using natural language commands.

## Features

- **Natural Language Control**: Describe tasks in plain English, e.g., "open google", "close cookie popup", "search for Python tutorials"
- **Persistent Browser Session**: Browser stays open between commands, enabling multi-step workflows
- **Visible Mode**: Browser window is visible so you can watch the automation in real-time
- **REPL Interface**: Continuous command loop with history support
- **Robust Error Handling**: Application continues running even if individual commands fail
- **Graceful Shutdown**: Clean exit with Ctrl+C or exit/quit commands
- **Multi-LLM Support**: Works with OpenAI, Gemini, NVIDIA, or any OpenAI-compatible API
- **Multi-Model Fallback**: Configure multiple models in .env; if one fails, automatically switches to the next
- **Browser Opens Immediately**: Browser launches on startup and waits for commands

## Requirements

- Python 3.10+
- LLM API access (OpenAI or compatible service)

## Installation

1. Clone or download the project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` file:
```env
# LLM API configuration
OPENAI_API_KEY=your_api_key_here

# Optional: Custom API Base URL (default: https://api.openai.com/v1)
OPENAI_API_BASE=https://api.openai.com/v1

# Optional: Model name (supports multiple models, comma-separated)
# If multiple models are specified, the system will automatically try the next one if one fails
# Example: MODEL_NAME=qwen/qwen3.5-122b-a10b,deepseek-chat,gpt-4o
MODEL_NAME=gpt-4o
```

**Note**: You can use any OpenAI-compatible service:
- NVIDIA: `OPENAI_API_BASE=https://integrate.api.nvidia.com/v1`
- Google Gemini: `OPENAI_API_BASE=https://generativelanguage.googleapis.com/v1beta/openai`
- DeepSeek: `OPENAI_API_BASE=https://api.deepseek.com/v1`
- Local models (Ollama, LM Studio): `OPENAI_API_BASE=http://localhost:11434/v1`

## Usage

Run the application:
```bash
python main.py
```

The browser will launch automatically and you'll see a command prompt. The browser window will open and wait for your commands.

### Example Commands

```
Command > go to google.com
Command > accept the cookie consent
Command > search for browser-use python library
Command > click the first result
Command > what is the current page title?
Command > go to bing.com
Command > exit
```

### Special Commands

- `help` - Show help information
- `status` - Show browser status
- `exit` / `quit` - Exit the program
- `Ctrl+C` - Force exit

## How It Works

1. Application starts and initializes the browser (visible mode) and LLM configuration
2. Uses browser-use's Agent to interpret and execute natural language commands
3. Agent analyzes the page DOM and decides which actions to take (click, type, navigate, etc.)
4. Browser session persists across commands - the Agent remembers previous context
5. Each command is added to the Agent's task list and executed sequentially

## Project Structure

```
.
├── main.py # Main application entry point
├── requirements.txt # Dependencies
├── .env # Configuration file (create this)
├── README.md # English documentation
├── README_zh.md # Chinese documentation
├── README_es.md # Spanish documentation
└── test_*.py # Test files (optional)
```

## Troubleshooting

1. **API Key Error**: Ensure `.env` file exists and `OPENAI_API_KEY` is set correctly
2. **Browser Launch Fails**: Check if another browser instance is running, or try restarting
3. **Command Fails**: Some complex pages may need more detailed commands; the LLM will try to interpret
4. **Import Errors**: Make sure you installed requirements with `pip install -r requirements.txt`
5. **Unicode Errors on Windows**: The application automatically configures UTF-8 encoding
6. **LLM JSON Parsing Errors**: The application now includes a fallback LLM and disables thinking mode for better compatibility with some models
7. **Browser State Not Persisting**: The application now uses `user_data_dir` to persist cookies, login sessions, and other browser state in the `browser_data/` directory

## Technical Details

- **browser-use version**: 0.12.1
- **Architecture**: Single persistent Agent instance with `keep_alive=True` browser profile
- **Multi-task support**: Uses `agent.add_new_task()` to queue commands without resetting browser state
- **Async/Await**: Full async implementation for responsive CLI
- **Browser Data Persistence**: Uses `user_data_dir` to store browser profile in `browser_data/` directory, preserving cookies, login sessions, and other browser state across sessions

## Notes

- First run downloads browser driver (Playwright) - this may take a moment
- Visible mode (`headless=False`) is recommended for debugging
- Some websites have anti-bot measures - use responsibly and respect terms of service
- Best used in testing environments; avoid automating production websites

## A Simple Test and Model Performance

### Test Command

```bash
python main.py -c "第一步、打开这个网页（番茄小说的小说管理界面）：https://fanqienovel.com/main/writer/chapter-manage/7601645527918201918&共和国特工?type=1 。第二步、根据网页内容判断上一次发布的最新章节序号，不需要翻页，默认显示的就是一定是最新章节。计算出你要发布的新一章序号（例如上一章是130，新章节就是131）。新一章对应的本地文件路径是：C:\Code\iNovel-v2.3\data\chapters\chapter-[序号].txt （注意替换实际的新章节序号，严禁修改目录结构，如果使用工具读取时报错找不到文件就停止操作，结束流程）。第三步、点击新建章节。第四步、在章节新建页面的填入工作，规则如下：【章节序号】计算出的新章节纯数字序号填到第___章之间的那个框（第一个可输入文本框）；【标题】请使用 read_local_file 工具，设置 start_line=1, end_line=1 读取第一行内容。你需要智能提取标题部分（去除"标题：""《""》"等字样），然后填入标题框(提示："请输入标题..."，第二个可输入文本框)；【正文】请直接使用 fill_from_file 动作，指定 index 为正文编辑框（提示"请输入正文..."的那个大文本框，第三个可输入文本框）的序号，设置 file_path 为刚才的文件路径，并且设置 start_line=3（从第二行开始读取全部正文），让系统直接填充，不要尝试自己复制粘贴正文内容。第五步、填入完毕后点击下一步。后续步骤处理弹窗：弹窗类型一、问有错别字未修改，不用理会，点击提交继续。弹窗类型二、问是否进行内容风险监测，点击确定。弹窗类型三、发布设置窗口，在是否使用AI的部分选择"否"(右边那个radiobox)，不要点击确认发布，然后暂停100秒后，退出。弹窗类型四、内容检测不合格，就退出流程，停止操作。弹窗类型五、提示本地服务器版本冲突什么，不用理会。"
```

> **Note**: This test only works with large models that support image input, otherwise it will definitely fail.

### Model Performance Results

| Model | Result | Time |
|-------|--------|------|
| Gemini 2.5 Flash-lite | ✅ Pass (1 error fixed) | Fast: 1:30 |
| Gemini 2.5 Flash | 🟢 Good | Fast: 1:30 |
| Gemini 3.0 Flash | 🟢 Good | Fast: 1:30 |
| Gemini 3.1 Flash Lite | 🟢 Good | Fast: 1:15 |
| *** Provided by ModelScope *** | | |
| Xiaomi MIMO V2 Flash | 🟢 Good | Slow: 3:15 |
| K2.5 | ✅ Pass (non-fatal error) | Medium: 2:13 |
| Qwen3.5 35B | ⚠️ Barely (last step error) | Fast: 1:12 |
| Qwen3.5 27B | 🟢 Good | Medium: 2:35 |
| Qwen3.5 122B | ✅ Pass (error fixed) | Fast: 1:25 |
| Qwen3.5 397B | ⚠️ Barely (last step error) | Fast: 1:20 |

## License

MIT License
