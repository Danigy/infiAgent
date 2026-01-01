# MLA-V3 Web UI

A simple web front-end interface for interacting with the MLA-V3 framework.
## Features

- 🎨 Modern conversation interface
- 🤖 Display currently executing Agent (with avatar)
- 📂 Display Task ID and Workspace path
- 📊 Real-time streaming output (JSONL event stream)
- 🔔 Human-in-Loop (HIL) interaction support: Automatically detects and responds to Agent's human interaction tasks
- 💬 Support for multi-line input and Enter to send
- 💾 Conversation history automatically saved to task_id/conversations/ directory
- 📁 Integrated file browser to view and manage task files

## Installation Dependencies

```bash
pip install flask flask-cors
```

Or add to requirements.txt:

```
flask
flask-cors
```

## Startup Methods

### Method 1: Using Convenience Script (Recommended)）

**Note**：The startup script will automatically launch the tool server (tool_server_lite), no manual startup required. On first run, you'll be prompted to set the workspace root path.

1. Start the server (will automatically start Web UI and tool server):
   - First run will prompt for workspace path
   - Press Enter to use current directory as workspace (same as CLI mode)
   - Or enter absolute path to specify custom workspace
   ```bash
   cd web_ui/server
   ./start.sh
   ```
   Or use unified management script:
   ```bash
   cd web_ui/server
   ./server start
   ```

2. Stop server (will stop both Web UI and tool server):
   ```bash
   cd web_ui/server
   ./stop.sh
   ```
   Or:
   ```bash
   cd web_ui/server
   ./server stop
   ```

3. Check server status:
   ```bash
   cd web_ui/server
   ./server status
   ```
   Will show running status of Web UI and tool server.

4. Restart server:
   ```bash
   cd web_ui/server
   ./server restart
   ```

5. Open browser and visit:
   ```
   http://localhost:22228
   ```
   
   **Server addresses**：
   - Web UI: http://localhost:22228
   - Tool server API: http://localhost:24243
   - Tool server documentation: http://localhost:24243/docs

### Method 2：Direct Python Execution (Traditional Method)

**Note**： If using this method, need to manually start tool server.

1. Start tool server (in one terminal):
   ```bash
   cd tool_server_lite
   python server.py
   ```

2. Start Web UI server (in another terminal):
   ```bash
   cd web_ui/server
   python server.py
   ```

3. Open browser and visit:
   ```
   http://localhost:22228
   ```

### Port Configuration

- **Web UI default port**: 22228（because macOS AirPlay may occupy port 5000)
- **Tool server default port**: 24243
- Can specify other ports via environment variables:
  ```bash
  cd web_ui/server
  PORT=8080 TOOL_PORT=8002 ./start.sh
  # or
  PORT=8080 TOOL_PORT=8002 ./server start
  ```

## Usage Instructions

### 1. Set Task ID

Enter the absolute path of the task directory in the top "Task ID" input box, for example:
```
/mla_task
```
or
```
/Users/username/Desktop/my_project
```

### 2. Agent Configuration

- Current version fixed to use alpha_agent and Default system
- No manual selection required, system automatically uses correct configuration

### 3. Input Task

Enter task description in the bottom input box, for example:
```
Help me find a paper about ECM
```

Then click the "Send" button or press Enter (Shift+Enter for new line).

### 4. View Output

Agent execution output will be displayed in real-time in the conversation window:
- Each message displays Agent avatar and name
- Different message types have different colors:
  - 🔧 Tool call (tool_call): Cyan
  - 🤖 Sub-agent call (agent_call): Blue
  - ✅ Success message: Cyan
  - ❌ Error message: Red
  - ⚠️ Warning message: Yellow
  - 📊 Result message: Orange
  - 💭 Thinking message: Purple

### 5. Human-in-Loop (HIL) Interaction

When Agent requires human input:
- Input box will automatically show red flashing effect
- Input box placeholder will display Agent instructions
- Send button automatically enabled (even if input box is empty)
- Enter response in input box and click Send
- Agent will continue task execution

**Workflow**：
1. Agent calls human_in_loop tool
2. Front-end automatically detects HIL task
3. Input box shows red flashing prompt
4. User enters response and sends
5. Agent continues execution

## Interface Description

### Top Control Bar
- **Task ID**: Task workspace directory path (supports task selection dropdown)
- **Agent**: Fixed to `alpha_agent`
- **System**: Fixed to `Default` system
- **File Browser**: Right side can browse and manage task files

### Conversation Window
- Displays all messages (user input and Agent output)
- Automatically scrolls to latest message
- Supports long text and multi-line display

### Input Area
- Text input box (supports multiple lines)
  - Normal state: Blue border
  - HIL waiting state: Red flashing border
- Send button
  - Automatically enabled when content present
  - Always enabled in HIL mode
- Status bar (displays running status and Workspace path)

## Technical Architecture

- **Backend**: Flask + Server-Sent Events (SSE)
- **Frontend**: Native HTML + CSS + JavaScript
- **Event Stream**: Directly parses JSONL event stream (`--jsonl` mode)
- **Streaming Transmission**: Uses SSE for real-time output
- **HIL Support**: Event triggering + intelligent polling detection mechanism
- **Data Storage**: Conversation history stored in `task_id/conversations/` directory

## File Structure

```
web_ui/
├── server/                    # Server-related files
│   ├── server.py              # Flask backend server
│   ├── start.sh               # Startup script (supports workspace configuration)
│   ├── stop.sh                # Stop script
│   └── users.yaml             # User authentication configuration
├── index.html                 # Frontend page
├── login.html                 # Login page
├── static/                    # Static resources
│   ├── style.css             # Style file
│   └── app.js                # JavaScript logic (includes HIL detection)
├── requirements.txt           # Python dependencies
└── README.md                 # Usage instructions
```

## Data Storage

### Conversation History

All conversation history and related data stored under task directory:

```
{task_id}/
├── conversations/             # Conversation history directory
│   ├── _stack.json           # Agent call stack
│   ├── _share_context.json   # Shared context
│   └── {agent_id}_actions.json  # Agent action history
├── chat_history.json         # Web UI chat records (frontend display)
└── latest_output.json        # Latest output (for quick preview)
```

**Note**：Deleting `task_id` directory will delete all related data, including conversation history.

## Troubleshooting

### 1. Cannot Connect to Server
- Check if server is running
- Check if port 5000 is occupied
- Check server terminal error messages

### 2. Agent Execution Failure
- Check if Task ID path is correct
- Check if tool server is running normally
- Check browser console error messages

### 3. Output Not Displayed
- Check browser console for JavaScript errors
- Check if SSE connection is normal (Network tab)
- Check server logs

### 4. HIL Task No Response
- Confirm tool server is running (check port 8001/8002)
- Check browser console for error messages
- Refresh page and retry

### 5. Workspace Path Issues
- Ensure path is absolute
- Check if path has write permissions
- Rerun `start.sh` to configure correct workspace

## Development Instructions

### Modify Port

Modify in `server.py`:
```python
port = int(os.environ.get('PORT', 5000))
```

Or via environment variable:
```bash
PORT=8080 python server.py
```

### Add New Agent Avatar

Add to `agentAvatars` object in `app.js`:
```javascript
const agentAvatars = {
    'your_agent': '🎯',
    // ...
};
```

### Customize Styles

Modify `static/style.css` file to customize interface styles.

## License

Same as main project.
