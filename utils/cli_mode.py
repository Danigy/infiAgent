#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive CLI Mode
"""

import os
import sys
from pathlib import Path
import subprocess
import threading
import queue
import signal
import time
import json
import hashlib
from datetime import datetime

try:
    from prompt_toolkit import PromptSession, print_formatted_text
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.patch_stdout import patch_stdout
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def t(key: str, lang: str = 'en') -> str:
    """Get text in specified language (global function)"""
    return TEXTS.get(lang, TEXTS['en']).get(key, key)


# Multilingual text configuration
TEXTS = {
    'en': {
        # System messages
        'select_agent_system': 'Select Agent System',
        'select_mode': 'Select Tool Execution Mode',
        'auto_mode': 'Auto Mode - All tools execute automatically (fast, risky)',
        'manual_mode': 'Manual Mode - File write/code exec/pip install need confirmation (safe)',
        'mode_set_auto': 'Set to: Auto Mode',
        'mode_set_manual': 'Set to: Manual Mode',
        'invalid_choice': 'Invalid choice, please enter',
        'default': 'default',
        
        # Banner
        'cli_title': 'MLA Agent - Interactive CLI',
        'work_dir': 'Work Directory',
        'default_agent': 'Default Agent',
        'available_agents': 'Available Agents',
        'usage': 'Usage',
        'usage_1': 'Enter task directly (use default Agent)',
        'usage_2': '@agent_name task (switch and use specified Agent)',
        'usage_3': 'HIL tasks will auto-prompt for response',
        'usage_4': 'Ctrl+C interrupt | /resume resume | /quit exit | /help help',
        
        # Commands
        'starting_task': 'Starting Task',
        'input': 'Input',
        'hint_resume': 'Hint: Enter /resume to resume, enter new content to start new task',
        'stopping_task': 'Stopping running task...',
        'task_stopped': 'Task stopped',
        'task_force_stopped': 'Task force stopped',
        'goodbye': 'Goodbye!',
        'available_agents_list': 'Available Agents',
        'current': 'current',
        'interrupting_task': 'Interrupting task...',
        'task_interrupted': 'Task interrupted',
        'no_running_task': 'No running task. Enter /quit to exit CLI',
        
        # HIL
        'hil_detected': 'HIL task detected! Press Enter to handle...',
        'hil_task': 'Human-in-Loop Task',
        'task_id': 'Task ID',
        'instruction': 'Instruction',
        'enter_response': 'Please enter your response (any text)',
        'skip_task': 'Enter /skip to skip this task',
        'hil_responded': 'HIL task responded',
        'content': 'Content',
        'hil_response_failed': 'HIL response failed, please retry',
        'hil_skipped': 'HIL task skipped',
        'response_empty': 'Response cannot be empty, please re-enter',
        
        # Tool confirmation
        'tool_confirm_detected': 'Tool execution request detected! Press Enter to confirm...',
        'tool_confirm_title': 'Tool Execution Confirmation',
        'tool_name': 'Tool Name',
        'confirm_id': 'Confirm ID',
        'parameters': 'Parameters',
        'choose_action': 'Choose action',
        'approve_tool': 'yes / y - Approve tool execution',
        'reject_tool': 'no / n  - Reject tool execution',
        'tool_approved': 'Tool approved',
        'tool_rejected': 'Tool rejected',
        'invalid_choice_yn': 'Invalid choice, please enter yes or no',
        
        # Resume
        'checking_task': 'Checking interrupted task...',
        'task_found': 'Interrupted task found',
        'agent': 'Agent',
        'task': 'Task',
        'interrupted_at': 'Interrupted at',
        'stack_depth': 'Stack depth',
        'resume_confirm': 'Resume this task? [y/N]',
        'resume_cancelled': 'Resume cancelled',
        'resuming_task': 'Resuming task...',
        
        # Pending task warning
        'pending_task_warning': 'Pending task detected, cannot start new task!',
        'hil_pending': 'HIL task waiting for response',
        'tool_confirm_pending': 'Tool confirmation waiting for processing',
        'press_enter_hint': 'Please press Enter to enter processing mode',
        
        # Toolbar
        'toolbar': '@agent switch | Ctrl+C interrupt | /resume resume | /quit exit',
        'toolbar_hil': 'HIL task waiting for response!',
    },
    'zh': {
        # System messages
        'select_agent_system': '选择 Agent 系统',
        'select_mode': '选择工具执行模式',
        'auto_mode': '自动模式 (Auto) - 所有工具自动执行（快速，但有风险）',
        'manual_mode': '手动模式 (Manual) - 文件写入、代码执行、包安装需要确认（安全）',
        'mode_set_auto': '已设置为: 自动模式 (Auto)',
        'mode_set_manual': '已设置为: 手动模式 (Manual)',
        'invalid_choice': '无效选择，请输入',
        'default': '默认',
        
        # Banner
        'cli_title': 'MLA Agent - 交互式 CLI',
        'work_dir': '工作目录',
        'default_agent': '默认Agent',
        'available_agents': '可用Agents',
        'usage': '使用说明',
        'usage_1': '直接输入任务（使用默认 Agent）',
        'usage_2': '@agent_name 任务（切换并使用指定 Agent）',
        'usage_3': 'HIL 任务出现时会自动提示，输入响应内容即可',
        'usage_4': 'Ctrl+C 中断任务 | /resume 恢复 | /quit 退出 | /help 帮助',
        
        # Commands
        'starting_task': '启动任务',
        'input': '输入',
        'hint_resume': '提示: 输入/resume回车可续跑，输入新内容开始新任务',
        'stopping_task': '正在停止运行中的任务...',
        'task_stopped': '任务已停止',
        'task_force_stopped': '任务已强制终止',
        'goodbye': '再见！',
        'available_agents_list': '可用 Agents',
        'current': '当前',
        'interrupting_task': '正在中断任务...',
        'task_interrupted': '任务已中断',
        'no_running_task': '没有运行中的任务。输入 /quit 退出 CLI',
        
        # HIL
        'hil_detected': '检测到 HIL 任务！请按回车处理...',
        'hil_task': '人类交互任务 (HIL)',
        'task_id': '任务ID',
        'instruction': '指令',
        'enter_response': '请输入您的响应（任何文本）',
        'skip_task': '输入 /skip 跳过此任务',
        'hil_responded': 'HIL 任务已响应',
        'content': '内容',
        'hil_response_failed': 'HIL 响应失败，请稍后重试',
        'hil_skipped': '已跳过此 HIL 任务',
        'response_empty': '响应内容不能为空，请重新输入',
        
        # Tool confirmation
        'tool_confirm_detected': '检测到工具执行请求！请按回车确认...',
        'tool_confirm_title': '工具执行确认请求',
        'tool_name': '工具名称',
        'confirm_id': '确认ID',
        'parameters': '参数',
        'choose_action': '选择操作',
        'approve_tool': 'yes / y - 批准执行此工具',
        'reject_tool': 'no / n  - 拒绝执行此工具',
        'tool_approved': '已批准执行工具',
        'tool_rejected': '已拒绝执行工具',
        'invalid_choice_yn': '无效选择，请输入 yes 或 no',
        
        # Resume
        'checking_task': '检查中断的任务...',
        'task_found': '发现中断的任务',
        'agent': 'Agent',
        'task': '任务',
        'interrupted_at': '中断于',
        'stack_depth': '栈深度',
        'resume_confirm': '是否恢复此任务？ [y/N]',
        'resume_cancelled': '已取消恢复',
        'resuming_task': '恢复任务...',
        
        # Pending task warning
        'pending_task_warning': '检测到待处理的任务，无法启动新任务！',
        'hil_pending': 'HIL 任务正在等待您的响应',
        'tool_confirm_pending': '工具确认请求正在等待您的处理',
        'press_enter_hint': '请直接按回车进入处理模式',
        
        # Toolbar
        'toolbar': '@agent 切换 | Ctrl+C 中断 | /resume 恢复 | /quit 退出',
        'toolbar_hil': '有HIL任务等待响应！',
    }
}


class InteractiveCLI:
    """Interactive command-line interface"""
    
    def __init__(self, task_id: str, agent_system: str = "Test_agent"):
        self.task_id = task_id
        self.agent_system = agent_system
        self.current_agent = "alpha_agent"
        self.current_process = None
        self.output_queue = queue.Queue()
        self.output_lines = []  # Save recent output
        self.max_output_lines = 20  # Keep at most 20 lines of output
        self.hil_mode = False  # Whether in HIL response mode
        self.current_hil_task = None  # Current HIL task
        self.pending_hil = None  # Pending HIL task (detected by background thread)
        self.hil_processing = False  # Whether currently processing HIL task (avoid duplicate detection)
        self.hil_check_interval = 2  # HIL check interval (seconds)
        self.stop_hil_checker = False  # Flag to stop HIL checker thread
        
        # Tool confirmation related
        self.pending_tool_confirmation = None  # Pending tool confirmation (detected by background thread)
        self.tool_confirmation_processing = False  # Whether currently processing tool confirmation
        self.auto_mode = None  # Permission mode (None=not set, True=auto, False=manual)
        
        # Language setting
        self.language = 'en'  # Default English
        
        # Rich console
        self.console = Console() if RICH_AVAILABLE else None
        
        # Load available agent list
        self.available_agents = self._load_available_agents()
        
        # Get tool server address
        self._load_tool_server_url()
        
        # Start background HIL checker thread
        self._start_hil_checker()
    
    def t(self, key: str) -> str:
        """Get text in current language"""
        return TEXTS.get(self.language, TEXTS['en']).get(key, key)
    
    def _load_available_agents(self):
        """Load Level 2/3 Agent list"""
        try:
            from utils.config_loader import ConfigLoader
            config_loader = ConfigLoader(self.agent_system)
            
            agents = []
            for name, config in config_loader.all_tools.items():
                if config.get("type") == "llm_call_agent":
                    level = config.get("level", 0)
                    if level in [1,2, 3]:
                        agents.append(name)
            
            return agents
        except:
            return ["alpha_agent"]
    
    def _load_tool_server_url(self):
        """Load tool server address"""
        try:
            import yaml
            config_path = Path(__file__).parent.parent / "config" / "run_env_config" / "tool_config.yaml"
            with open(config_path, 'r', encoding='utf-8') as f:
                tool_config = yaml.safe_load(f)
            self.server_url = tool_config.get('tools_server', 'http://127.0.0.1:8001').rstrip('/')
        except Exception:
            self.server_url = 'http://127.0.0.1:8001'
    
    def _check_hil_task(self) -> dict:
        """Check if current workspace has pending HIL tasks"""
        try:
            import requests
            response = requests.get(
                f"{self.server_url}/api/hil/workspace/{self.task_id}",
                timeout=2
            )
            if response.status_code == 200:
                return response.json()
            return {"found": False}
        except Exception:
            return {"found": False}
    
    def _respond_hil_task(self, hil_id: str, response: str) -> bool:
        """Respond to HIL task"""
        try:
            import requests
            resp = requests.post(
                f"{self.server_url}/api/hil/respond/{hil_id}",
                json={"response": response},
                timeout=5
            )
            result = resp.json()
            return result.get('success', False)
        except Exception:
            return False
    
    def _check_tool_confirmation(self) -> dict:
        """Check if current workspace has pending tool confirmation requests"""
        try:
            import requests
            response = requests.get(
                f"{self.server_url}/api/tool-confirmation/workspace/{self.task_id}",
                timeout=2
            )
            if response.status_code == 200:
                return response.json()
            return {"found": False}
        except Exception:
            return {"found": False}
    
    def _respond_tool_confirmation(self, confirm_id: str, approved: bool) -> bool:
        """Respond to tool confirmation request"""
        try:
            import requests
            resp = requests.post(
                f"{self.server_url}/api/tool-confirmation/respond/{confirm_id}",
                json={"approved": approved},
                timeout=5
            )
            result = resp.json()
            return result.get('success', False)
        except Exception:
            return False
    
    def _get_interrupted_task(self) -> dict:
        """Get interrupted task (check stack)"""
        try:
            # Calculate task_id hash (consistent with hierarchy_manager)
            task_hash = hashlib.md5(self.task_id.encode()).hexdigest()[:8]  # 8 digits, not 12
            
            # Cross-platform path handling
            task_folder = Path(self.task_id).name if (os.sep in self.task_id or '/' in self.task_id or '\\' in self.task_id) else self.task_id
            task_name = f"{task_hash}_{task_folder}"
            
            # Stack file location (consistent with hierarchy_manager)
            conversations_dir = Path.home() / "mla_v3" / "conversations"
            stack_file = conversations_dir / f"{task_name}_stack.json"
            
            if not stack_file.exists():
                return {"found": False, "message": f"No interrupted task found (file does not exist: {stack_file})"}
            
            # Read stack
            with open(stack_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stack = data.get("stack", [])
            
            if not stack:
                return {"found": False, "message": "No interrupted task (stack empty)"}
            
            # Get bottom task (initial user input)
            bottom_task = stack[0]
            agent_name = bottom_task.get("agent_name")
            user_input = bottom_task.get("user_input")
            
            if not agent_name or not user_input:
                return {"found": False, "message": "Task data incomplete"}
            
            return {
                "found": True,
                "agent_name": agent_name,
                "user_input": user_input,
                "interrupted_at": bottom_task.get("start_time", "Unknown"),
                "stack_depth": len(stack)
            }
        
        except Exception as e:
            return {"found": False, "message": f"Failed to read task: {e}"}
    
    def _start_hil_checker(self):
        """Start background HIL/tool confirmation checker thread"""
        def hil_checker_thread():
            while not self.stop_hil_checker:
                try:
                    # Check HIL tasks
                    if not self.pending_hil and not self.hil_processing:
                        hil_task = self._check_hil_task()
                        if hil_task.get("found"):
                            # Found new HIL task
                            self.pending_hil = hil_task
                            # Print alert sound (ASCII bell) and visible prompt
                            print("\n\n\a")  # \a is bell symbol
                            print("\n" + "="*80)
                            print(f"🔔🔔🔔 {self.t('hil_detected')} 🔔🔔🔔")
                            print("="*80 + "\n")
                    
                    # Check tool confirmation requests (only in manual mode)
                    if self.auto_mode == False and not self.pending_tool_confirmation and not self.tool_confirmation_processing:
                        tool_confirmation = self._check_tool_confirmation()
                        if tool_confirmation.get("found"):
                            # Found new tool confirmation request
                            self.pending_tool_confirmation = tool_confirmation
                            # Print alert sound and visible prompt
                            print("\n\n\a")
                            print("\n" + "="*80)
                            print(f"⚠️⚠️⚠️ {self.t('tool_confirm_detected')} ⚠️⚠️⚠️")
                            print("="*80 + "\n")
                except Exception:
                    pass
                
                # Wait before checking again
                time.sleep(self.hil_check_interval)
        
        thread = threading.Thread(target=hil_checker_thread, daemon=True)
        thread.start()
    
    def _show_hil_prompt(self, hil_id: str, instruction: str):
        """Display HIL prompt interface"""
        print("\n" + "="*80)
        print(f"🔔 {self.t('hil_task')}")
        print("="*80)
        print(f"📝 {self.t('task_id')}: {hil_id}")
        print(f"📋 {self.t('instruction')}: {instruction}")
        print("="*80)
        print(f"💡 {self.t('enter_response')}")
        print(f"   {self.t('skip_task')}")
        print("="*80 + "\n")
    
    def _show_tool_confirmation_prompt(self, confirm_id: str, tool_name: str, arguments: dict):
        """Display tool confirmation interface"""
        print("\n" + "="*80)
        print(f"⚠️  {self.t('tool_confirm_title')}")
        print("="*80)
        print(f"🔧 {self.t('tool_name')}: {tool_name}")
        print(f"📝 {self.t('confirm_id')}: {confirm_id}")
        print(f"📋 {self.t('parameters')}:")
        for key, value in arguments.items():
            # Truncate overly long parameter values
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            print(f"     {key}: {value_str}")
        print("="*80)
        print(f"💡 {self.t('choose_action')}:")
        print(f"   {self.t('approve_tool')}")
        print(f"   {self.t('reject_tool')}")
        print("="*80 + "\n")
    
    def get_banner_text(self):
        """Get banner text (for fixed top display)"""
        return (
            "="*80 + "\n" +
            f"🤖 {self.t('cli_title')}\n" +
            "="*80 + "\n" +
            f"📂 {self.t('work_dir')}: {self.task_id}\n" +
            f"🤖 {self.t('default_agent')}: {self.current_agent}\n" +
            f"📋 {self.t('available_agents')}: {', '.join(self.available_agents[:3])}{'...' if len(self.available_agents) > 3 else ''}\n" +
            "-"*80 + "\n" +
            f"💡 {self.t('usage')}:\n" +
            f"  - {self.t('usage_1')}\n" +
            f"  - {self.t('usage_2')}\n" +
            f"  - 🔔 {self.t('usage_3')}\n" +
            f"  - {self.t('usage_4')}\n" +
            "-"*80 + "\n"
        )
    
    def show_banner(self):
        """Display welcome message (initially)"""
        if RICH_AVAILABLE:
            self.console.clear()
            
            # Create top Panel
            header_table = Table.grid(padding=(0, 2))
            header_table.add_column(style="cyan")
            header_table.add_column()
            
            header_table.add_row(f"📂 {self.t('work_dir')}:", self.task_id)
            header_table.add_row(f"🤖 {self.t('default_agent')}:", f"[bold green]{self.current_agent}[/]")
            header_table.add_row(f"📋 {self.t('available_agents')}:", ", ".join(self.available_agents[:4]) + ("..." if len(self.available_agents) > 4 else ""))
            
            self.console.print(Panel(
                header_table,
                title=f"[bold blue]🤖 {self.t('cli_title')}[/]",
                border_style="blue"
            ))
            
            # Usage instructions
            help_text = Text()
            help_text.append(f"💡 {self.t('usage')}:\n", style="bold yellow")
            help_text.append(f"  • {self.t('usage_1')}\n")
            help_text.append(f"  • {self.t('usage_2')}\n")
            help_text.append(f"  • 🔔 {self.t('usage_3')}\n", style="cyan")
            help_text.append(f"  • {self.t('usage_4')}\n")
            
            self.console.print(Panel(help_text, border_style="dim"))
            print()
        else:
            # Fallback to simple mode
            os.system('clear' if os.name != 'nt' else 'cls')
            print(self.get_banner_text())
    
    def parse_input(self, user_input: str):
        """
        Parse user input
        
        Returns:
            (agent_name, task_description)
        """
        user_input = user_input.strip()
        
        # Check if agent specified
        if user_input.startswith('@'):
            parts = user_input[1:].split(None, 1)
            if len(parts) == 2:
                agent_name, task = parts
                # Verify agent exists
                if agent_name in self.available_agents:
                    return agent_name, task
                else:
                    print(f"⚠️  Agent '{agent_name}' does not exist, using default Agent")
                    return self.current_agent, user_input
            elif len(parts) == 1:
                # Only @agent_name, no task
                agent_name = parts[0]
                if agent_name in self.available_agents:
                    self.current_agent = agent_name
                    print(f"✅ Switched to: {agent_name}")
                    return None, None
                else:
                    print(f"⚠️  Agent '{agent_name}' does not exist")
                    return None, None
        
        # No @, use default agent
        return self.current_agent, user_input
    
    def stop_current_task(self):
        """Stop currently running task"""
        if self.current_process and self.current_process.poll() is None:
            try:
                if sys.platform == 'win32':
                    # Windows: Send Ctrl+Break signal
                    self.current_process.send_signal(signal.CTRL_BREAK_EVENT)
                    try:
                        self.current_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # If signal ineffective, force terminate
                        self.current_process.terminate()
                        self.current_process.wait(timeout=1)
                else:
                    # Unix/Mac: Use terminate (send SIGTERM)
                    self.current_process.terminate()
                    self.current_process.wait(timeout=3)
                print("\n⚠️  Previous task terminated\n")
            except Exception as e:
                # Last resort: force kill
                try:
                    self.current_process.kill()
                    self.current_process.wait(timeout=1)
                except (subprocess.TimeoutExpired, ProcessLookupError, PermissionError):
                    pass
    
    def run_task(self, agent_name: str, user_input: str):
        """
        Run task in background (JSONL mode)
        Keep foreground input available
        """
        # Terminate current task (if any)
        self.stop_current_task()
        
        print(f"\n{'='*80}")
        print(f"🤖 {self.t('starting_task')}: {agent_name}")
        print(f"📝 {self.t('input')}: {user_input}")
        print(f"💡 {self.t('hint_resume')}")
        print(f"{'='*80}\n")
        
        # Use current Python interpreter to call start.py (avoid venv path issues)
        start_py = Path(__file__).parent.parent / "start.py"
        
        # Windows requires special process creation flags to support signal handling
        popen_kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'encoding': 'utf-8',
            'errors': 'replace',
            'bufsize': 0  # No buffering, real-time output
        }
        
        if sys.platform == 'win32':
            # Windows: Create new process group, allow sending Ctrl+Break
            popen_kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        
        # Build command arguments (use Python interpreter to directly run start.py)
        cmd_args = [
            sys.executable,
            str(start_py),
                '--task_id', self.task_id,
                '--agent_name', agent_name,
                '--user_input', user_input,
                '--agent_system', self.agent_system,
                '--jsonl'  # JSONL mode, real-time streaming output
        ]
        
        # Add permission mode parameter
        if self.auto_mode is not None:
            cmd_args.extend(['--auto-mode', 'true' if self.auto_mode else 'false'])
        
        # Start subprocess (JSONL mode - real-time streaming output)
        self.current_process = subprocess.Popen(
            cmd_args,
            **popen_kwargs
        )
        
        # Background thread reads output (JSONL mode, parse and display)
        def read_output():
            try:
                import json
                for line in self.current_process.stdout:
                    if not line:
                        continue
                    line = line.rstrip('\n')
                    if not line.strip():
                        continue
                    
                    try:
                        # Parse JSONL event
                        event = json.loads(line)
                        
                        # Display all events (without truncation)
                        if event['type'] == 'token':
                            text = event['text']
                            # Display all text completely
                            display_line = f"  {text}"
                            
                            self.output_lines.append(display_line)
                            if len(self.output_lines) > self.max_output_lines:
                                self.output_lines.pop(0)
                            print(display_line)
                        
                        elif event['type'] == 'result':
                            # Display complete result
                            summary = event.get('summary', '')
                            
                            print(f"\n{'='*80}")
                            print("📊 Execution result:")
                            print(f"{'='*80}")
                            print(summary)  # Complete display
                            print(f"{'='*80}\n")
                            
                            # Brief summary to output history
                            self.output_lines.append(f"📊 Result: {summary[:100]}...")
                        
                        elif event['type'] == 'end':
                            status_icon = "✅" if event.get('status') == 'ok' else "❌"
                            duration_sec = event.get('duration_ms', 0) / 1000
                            display_line = f"{status_icon} Task completed ({duration_sec:.1f}s)"
                            self.output_lines.append(display_line)
                            print(display_line)
                            print()
                    
                    except json.JSONDecodeError:
                        # Not valid JSON, skip
                        pass
            except Exception:
                pass
        
        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()

        # Read stderr, prevent pipe blocking (but don't display, since JSONL mode redirects print to stderr)
        def read_stderr():
            try:
                for err in self.current_process.stderr:
                    if not err:
                        continue
                    # Silently consume stderr, prevent pipe from filling and blocking
                    # Only display when encountering real error keywords
                    err = err.rstrip('\n')
                    if any(keyword in err for keyword in ['Error:', 'Exception:', 'Traceback', 'CRITICAL', 'FATAL']):
                        error_line = f"⚠️ {err[:200]}"
                        self.output_lines.append(error_line)
                        if len(self.output_lines) > self.max_output_lines:
                            self.output_lines.pop(0)
                        print(error_line)
            except Exception:
                pass

        thread_err = threading.Thread(target=read_stderr, daemon=True)
        thread_err.start()
    
    def get_bottom_toolbar(self):
        """Get bottom toolbar text"""
        # Check for HIL tasks (don't check frequently to avoid performance issues)
        try:
            hil_task = self._check_hil_task()
            if hil_task.get("found"):
                return HTML(
                    f'<style bg="ansired" fg="ansiwhite"> 🔔 {self.t("toolbar_hil")} </style>'
                )
        except:
            pass
        
        return HTML(
            f'<style bg="ansiblue" fg="ansiwhite"> 💡 {self.t("toolbar")} </style>'
        )
    
    def run(self):
        """Run interactive CLI"""
        self.show_banner()
        
        # Ask user to select permission mode
        print("\n" + "="*80)
        print(f"🔐 {self.t('select_mode')}")
        print("="*80)
        print(f"1. {self.t('auto_mode')}")
        print(f"2. {self.t('manual_mode')}")
        print("="*80)
        
        while self.auto_mode is None:
            mode_input = input(f"{self.t('invalid_choice')} [1/2] ({self.t('default')}: 2): ").strip()
            if not mode_input or mode_input == '2':
                self.auto_mode = False
                print(f"✅ {self.t('mode_set_manual')}\n")
            elif mode_input == '1':
                self.auto_mode = True
                print(f"✅ {self.t('mode_set_auto')}\n")
            else:
                print(f"❌ {self.t('invalid_choice')} 1 {self.t('default')} 2\n")
        
        # Use prompt_toolkit (if available)
        if PROMPT_TOOLKIT_AVAILABLE:
            # Create auto-completion
            agent_completions = ['@' + agent for agent in self.available_agents]
            completer = WordCompleter(
                agent_completions + ['/quit', '/exit', '/help', '/agents', '/resume', '/zh', '/en'],
                ignore_case=True,
                sentence=True
            )
            
            session = PromptSession(
                completer=completer,
                bottom_toolbar=self.get_bottom_toolbar
            )
        
        while True:
            try:
                # Check for pending HIL tasks (detected by background thread)
                if self.pending_hil:
                    hil_task = self.pending_hil
                    self.pending_hil = None  # Clear flag
                    self.hil_processing = True  # Mark as processing to avoid duplicate detection by background thread
                    
                    # Enter HIL response mode
                    hil_id = hil_task["hil_id"]
                    instruction = hil_task["instruction"]
                    
                    # Display HIL task information
                    self._show_hil_prompt(hil_id, instruction)
                    
                    # Wait for user response
                    if PROMPT_TOOLKIT_AVAILABLE:
                        with patch_stdout():
                            user_response = session.prompt(f"[{self.current_agent}] HIL response > ").strip()
                    else:
                        user_response = input(f"[{self.current_agent}] HIL response > ").strip()
                    
                    if not user_response:
                        print(f"⚠️  {self.t('response_empty')}")
                        self.pending_hil = hil_task  # Restore task, continue processing next time
                        self.hil_processing = False  # Clear processing flag
                        continue
                    
                    if user_response == '/skip':
                        print(f"⏭️  {self.t('hil_skipped')}\n")
                        self.hil_processing = False  # Clear processing flag
                        continue
                    
                    # Submit response
                    if self._respond_hil_task(hil_id, user_response):
                        print(f"✅ {self.t('hil_responded')}")
                        print(f"   {self.t('content')}: {user_response[:100]}{'...' if len(user_response) > 100 else ''}\n")
                    else:
                        print(f"❌ {self.t('hil_response_failed')}\n")
                    
                    self.hil_processing = False  # Clear processing flag, allow detection of new HIL tasks
                    continue
                
                # Check for pending tool confirmation requests
                if self.pending_tool_confirmation:
                    tool_confirmation = self.pending_tool_confirmation
                    self.pending_tool_confirmation = None  # Clear flag
                    self.tool_confirmation_processing = True  # Mark as processing
                    
                    # Get confirmation information
                    confirm_id = tool_confirmation["confirm_id"]
                    tool_name = tool_confirmation["tool_name"]
                    arguments = tool_confirmation["arguments"]
                    
                    # Display tool confirmation interface
                    self._show_tool_confirmation_prompt(confirm_id, tool_name, arguments)
                    
                    # Wait for user choice
                    if PROMPT_TOOLKIT_AVAILABLE:
                        with patch_stdout():
                            user_choice = session.prompt(f"[{self.current_agent}] Confirm [yes/no] > ").strip().lower()
                    else:
                        user_choice = input(f"[{self.current_agent}] Confirm [yes/no] > ").strip().lower()
                    
                    if not user_choice:
                        print(f"⚠️  {self.t('invalid_choice_yn')}")
                        self.pending_tool_confirmation = tool_confirmation  # Restore task
                        self.tool_confirmation_processing = False
                        continue
                    
                    # Process user choice
                    if user_choice in ['yes', 'y']:
                        # Approve execution
                        if self._respond_tool_confirmation(confirm_id, True):
                            print(f"✅ {self.t('tool_approved')}: {tool_name}\n")
                        else:
                            print(f"❌ {self.t('hil_response_failed')}\n")
                    elif user_choice in ['no', 'n']:
                        # Reject execution
                        if self._respond_tool_confirmation(confirm_id, False):
                            print(f"❌ {self.t('tool_rejected')}: {tool_name}\n")
                        else:
                            print(f"❌ {self.t('hil_response_failed')}\n")
                    else:
                        print(f"⚠️  {self.t('invalid_choice_yn')}")
                        self.pending_tool_confirmation = tool_confirmation  # Restore task
                        self.tool_confirmation_processing = False
                        continue
                    
                    self.tool_confirmation_processing = False
                    continue
                
                # Normal mode: display prompt
                if PROMPT_TOOLKIT_AVAILABLE:
                    # Use patch_stdout to ensure task output doesn't affect input
                    with patch_stdout():
                        user_input = session.prompt(f"[{self.current_agent}] > ").strip()
                else:
                    user_input = input(f"[{self.current_agent}] > ").strip()
                
                if not user_input:
                    continue
                
                # Handle management commands (prioritized, unaffected by pending tasks)
                if user_input in ['/quit', '/exit', '/q']:
                    # Stop HIL checker thread
                    self.stop_hil_checker = True
                    
                    # Terminate running task
                    if self.current_process and self.current_process.poll() is None:
                        print("\n⏹️  Stopping running task...")
                        try:
                            if sys.platform == 'win32':
                                self.current_process.send_signal(signal.CTRL_BREAK_EVENT)
                                try:
                                    self.current_process.wait(timeout=2)
                                except subprocess.TimeoutExpired:
                                    self.current_process.terminate()
                                    self.current_process.wait(timeout=1)
                            else:
                                self.current_process.terminate()
                                self.current_process.wait(timeout=3)
                            print("✅ Task stopped")
                        except (subprocess.TimeoutExpired, ProcessLookupError):
                            try:
                                self.current_process.kill()
                                print("✅ Task force stopped")
                            except (ProcessLookupError, PermissionError):
                                pass
                    print("\n👋 Goodbye!\n")
                    break
                
                if user_input == '/help':
                    # Clear screen and redisplay banner
                    os.system('clear' if os.name != 'nt' else 'cls')
                    print(self.get_banner_text())
                    continue
                
                if user_input == '/agents':
                    print("\n📋 Available Agents:")
                    for i, agent in enumerate(self.available_agents, 1):
                        mark = " (current)" if agent == self.current_agent else ""
                        print(f"  {i}. {agent}{mark}")
                    print()
                    continue
                
                if user_input == '/resume':
                    # Resume interrupted task
                    print(f"\n🔍 {self.t('checking_task')}")
                    interrupted = self._get_interrupted_task()
                    
                    if not interrupted["found"]:
                        print(f"❌ {interrupted['message']}\n")
                        continue
                    
                    # Display task information
                    print(f"\n{'='*80}")
                    print(f"📋 {self.t('task_found')}")
                    print(f"{'='*80}")
                    print(f"🤖 {self.t('agent')}: {interrupted['agent_name']}")
                    print(f"📝 {self.t('task')}: {interrupted['user_input'][:100]}{'...' if len(interrupted['user_input']) > 100 else ''}")
                    print(f"⏸️  {self.t('interrupted_at')}: {interrupted['interrupted_at']}")
                    print(f"📊 {self.t('stack_depth')}: {interrupted['stack_depth']}")
                    print(f"{'='*80}\n")
                    
                    # Confirm resume
                    confirm = input(f"{self.t('resume_confirm')} ").strip().lower()
                    if confirm not in ['y', 'yes']:
                        print(f"⏭️  {self.t('resume_cancelled')}\n")
                        continue
                    
                    # Resume task
                    print(f"\n▶️  {self.t('resuming_task')}\n")
                    self.run_task(interrupted['agent_name'], interrupted['user_input'])
                    continue
                
                if user_input == '/zh':
                    # Switch to Chinese
                    self.language = 'zh'
                    print("\n✅ Switched to Chinese\n")
                    continue
                
                if user_input == '/en':
                    # Switch to English
                    self.language = 'en'
                    print("\n✅ Switched to English\n")
                    continue
                
                # Before executing new task, check for pending HIL or tool confirmation
                # Prevent users from accidentally entering content instead of pressing Enter to handle pending tasks
                if self.pending_hil or self.pending_tool_confirmation:
                    print("\n" + "="*80)
                    print(f"⚠️  {self.t('pending_task_warning')}")
                    print("="*80)
                    if self.pending_hil:
                        print(f"📌 {self.t('hil_pending')}")
                    if self.pending_tool_confirmation:
                        print(f"📌 {self.t('tool_confirm_pending')}")
                    print("="*80)
                    print(f"💡 {self.t('press_enter_hint')}")
                    print("="*80 + "\n")
                    continue
                
                # Parse input
                agent_name, task = self.parse_input(user_input)
                
                if agent_name and task:
                    # Add timestamp to task end
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    task_with_timestamp = f"{task} [Time: {timestamp}]"
                    
                    # Execute task
                    self.run_task(agent_name, task_with_timestamp)
                
            except KeyboardInterrupt:
                # Ctrl+C: Terminate current task but don't exit CLI
                if self.current_process and self.current_process.poll() is None:
                    print("\n\n⚠️  Interrupting task...")
                    try:
                        if sys.platform == 'win32':
                            # Windows: Send Ctrl+Break signal
                            self.current_process.send_signal(signal.CTRL_BREAK_EVENT)
                            try:
                                self.current_process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                self.current_process.terminate()
                                try:
                                    self.current_process.wait(timeout=1)
                                except (subprocess.TimeoutExpired, ProcessLookupError):
                                    self.current_process.kill()
                        else:
                            # Unix/Mac: Use terminate
                            self.current_process.terminate()
                            try:
                                self.current_process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                self.current_process.kill()
                    except Exception:
                        try:
                            self.current_process.kill()
                        except (ProcessLookupError, PermissionError):
                            pass
                    print("✅ Task interrupted\n")
                    print("💡 Enter /resume to resume, enter new content to start new task\n")
                else:
                    print("\n\n💡 No running task. Enter /quit to exit CLI\n")
                continue
            except EOFError:
                # Ctrl+D: Exit
                # Stop HIL checker thread
                self.stop_hil_checker = True
                
                if self.current_process and self.current_process.poll() is None:
                    print("\n\n⏹️  Stopping running task...")
                    try:
                        if sys.platform == 'win32':
                            self.current_process.send_signal(signal.CTRL_BREAK_EVENT)
                            try:
                                self.current_process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                self.current_process.terminate()
                                self.current_process.wait(timeout=1)
                        else:
                            self.current_process.terminate()
                            self.current_process.wait(timeout=3)
                    except (subprocess.TimeoutExpired, ProcessLookupError, PermissionError):
                        try:
                            self.current_process.kill()
                        except (ProcessLookupError, PermissionError):
                            pass
                print("\n\n👋 Goodbye!\n")
                break


def get_available_agent_systems():
    """Get available Agent system list"""
    try:
        # Find config/agent_library/ directory
        project_root = Path(__file__).parent.parent
        agent_library_dir = project_root / "config" / "agent_library"
        
        if not agent_library_dir.exists():
            return ["Test_agent"]
        
        # Get all subdirectories as available systems
        systems = []
        for item in agent_library_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                systems.append(item.name)
        
        return sorted(systems) if systems else ["Test_agent"]
    
    except Exception:
        return ["Test_agent"]


def start_cli_mode(agent_system: str = None, language: str = 'en'):
    """Start interactive CLI mode"""
    # task_id = current directory
    task_id = os.path.abspath(os.getcwd())
    
    # If agent_system not specified, let user choose
    if agent_system is None:
        available_systems = get_available_agent_systems()
        
        print("\n" + "="*80)
        print(f"🤖 {t('select_agent_system', language)}")
        print("="*80)
        
        for i, system in enumerate(available_systems, 1):
            print(f"{i}. {system}")
        
        print("="*80)
        
        while True:
            choice = input(f"{t('invalid_choice', language)} [1-{len(available_systems)}] ({t('default', language)}: 1): ").strip()
            
            if not choice:
                agent_system = available_systems[0]
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_systems):
                    agent_system = available_systems[idx]
                    break
                else:
                    print(f"❌ {t('invalid_choice', language)} 1-{len(available_systems)}\n")
            except ValueError:
                print(f"❌ {t('invalid_choice', language)} 1-{len(available_systems)}\n")
        
        if language == 'zh':
            print(f"✅ Selected: {agent_system}\n")
        else:
            print(f"✅ Selected: {agent_system}\n")
    
    cli = InteractiveCLI(task_id, agent_system)
    cli.language = language  # Set language
    cli.run()


if __name__ == "__main__":
    start_cli_mode()
