#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLA V3 Startup Script
Using the new XML-structured context system
"""

import sys
import argparse
from pathlib import Path
import os

# Windows console UTF-8 encoding support (solves emoji display issues)
if sys.platform == 'win32':
    try:
        # Set console code page to UTF-8
        import codecs
        # Use line buffering to ensure immediate output per line
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        # Force unbuffered mode
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True, write_through=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True, write_through=True)
    except Exception:
        pass

# Check PATH configuration on first import (only in non-import mode)
if __name__ == "__main__" and not hasattr(sys, '_mla_path_checked'):
    sys._mla_path_checked = True
    try:
        import site
        # Get user-level Scripts directory
        if sys.platform == 'win32':
            user_base = site.USER_BASE
            if user_base:
                scripts_dir = os.path.join(user_base, 'Scripts')
            else:
                scripts_dir = None
        else:
            user_base = site.USER_BASE
            if user_base:
                scripts_dir = os.path.join(user_base, 'bin')
            else:
                scripts_dir = None
        
        if scripts_dir and os.path.exists(scripts_dir):
            # Check if it's in PATH
            path_env = os.environ.get('PATH', '')
            path_dirs = path_env.split(os.pathsep)
            scripts_dir_normalized = os.path.normpath(scripts_dir).lower()
            in_path = any(os.path.normpath(p).lower() == scripts_dir_normalized for p in path_dirs)
            
            if not in_path:
                print("\n" + "="*80, file=sys.stderr)
                print("[Tip] To use the 'mla-agent' command directly, run: python check_path.py", file=sys.stderr)
                print("="*80 + "\n", file=sys.stderr)
    except Exception:
        pass

# Add project root directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config_loader import ConfigLoader
from core.hierarchy_manager import get_hierarchy_manager
from core.agent_executor import AgentExecutor


def main():
    """Main function"""
    import time
    import uuid
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MLA V3 - Multi-Level Agent System')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # respond subcommand (HIL response)
    respond_parser = subparsers.add_parser('respond', help='Respond to HIL task')
    respond_parser.add_argument('hil_id', type=str, help='HIL task ID')
    respond_parser.add_argument('response', type=str, help='User response content (can be any text)')
    # Main command arguments
    parser.add_argument('--task_id', type=str, help='Task ID (absolute path, used as workspace)')
    parser.add_argument('--agent_system', type=str, default='Default', help='Agent system name')
    #parser.add_argument('--agent_system', type=str, default='Test_agent', help='Agent system name')
    parser.add_argument('--agent_name', type=str, default='alpha_agent', help='Agent name to start')
    parser.add_argument('--user_input', type=str, help='User input/task description')
    parser.add_argument('--jsonl', action='store_true', help='Enable JSONL event output mode (for VS Code plugin integration)')
    parser.add_argument('--cli', action='store_true', help='Launch interactive CLI mode')
    parser.add_argument('--test', action='store_true', help='Run default test task')
    parser.add_argument('--config-show', action='store_true', help='Display current configuration')
    parser.add_argument('--config-set', nargs=2, metavar=('KEY', 'VALUE'), help='Set configuration item (e.g., api_key "YOUR_KEY")')
    parser.add_argument('--config-file', type=str, help='Use custom configuration file path')
    parser.add_argument('--force-new', action='store_true', help='Force clear all state and start new task')
    parser.add_argument('--auto-mode', type=str, choices=['true', 'false'], help='Tool execution mode: true=auto execute, false=requires confirmation')
    
    args = parser.parse_args()
    
    # Windows command line argument encoding fix
    if sys.platform == 'win32' and args.user_input:
        try:
            # Attempt to fix Windows command line encoding issues
            # Scenario: Windows cmd/PowerShell might incorrectly parse UTF-8 characters as Latin-1
            original = args.user_input
            fixed = args.user_input.encode('latin-1').decode('utf-8')
            # Apply only if the fix appears more reasonable (avoid breaking normal input)
            if fixed != original:
                args.user_input = fixed
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError) as e:
            # If fix fails, keep as-is (doesn't affect normal use)
            # Optional: log for debugging
            # print(f"[Debug] Encoding fix failed: {e}", file=sys.stderr)
            pass
    
    # Handle respond command
    if args.command == 'respond':
        import requests
        import yaml
        
        # Read tool server address
        config_path = Path(__file__).parent / "config" / "run_env_config" / "tool_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            tool_config = yaml.safe_load(f)
        server_url = tool_config.get('tools_server', 'http://127.0.0.1:8001').rstrip('/')
        
        # Call HIL response API
        try:
            response = requests.post(
                f"{server_url}/api/hil/respond/{args.hil_id}",
                json={"response": args.response},
                timeout=5
            )
            result = response.json()
            
            if result.get('success'):
                print(f"✅ HIL task responded: {args.hil_id}")
                print(f"   Content: {args.response}")
                return 0
            else:
                print(f"❌ Response failed: {result.get('error', 'Unknown error')}")
                return 1 
        except Exception as e:
            print(f"❌ Failed to connect to tool server: {e}")
            return 1
    
    # Handle CLI mode
    if args.cli:
        from utils.cli_mode import start_cli_mode
        # Do not pass agent_system, let user choose in CLI
        start_cli_mode()
        return 0
    
    # Handle configuration commands (priority)
    if args.config_show:
        from utils.config_manager import show_config
        show_config()
        return 0
    
    if args.config_set:
        from utils.config_manager import set_config
        set_config(args.config_set[0], args.config_set[1])
        return 0
    
    # Initialize event emitter
    from utils.event_emitter import init_event_emitter
    emitter = init_event_emitter(enabled=args.jsonl)
    
    # JSONL mode: Redirect all print to stderr
    if args.jsonl:
        sys.stdout_orig = sys.stdout
        sys.stderr_orig = sys.stderr
        # All print output goes to stderr
        sys.stdout = sys.stderr
    
    # If no arguments provided or --test specified, use default test
    if args.test or (not args.task_id and not args.user_input):
        if not args.jsonl:
            print("🧪 Using default test mode")
        # Cross-platform default task_id: use test directory under user home
        default_task_dir = Path.home() / "mla_v3" / "task_test"
        default_task_dir.mkdir(parents=True, exist_ok=True)
        args.task_id = args.task_id or str(default_task_dir)
        args.user_input = args.user_input or "What task was just completed?"
    
    # Check required parameters
    if not args.task_id or not args.user_input:
        parser.error("Need to provide --task_id and --user_input, or use --test to run default test")
        return 1
    
    # Generate call_id
    call_id = f"c-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    t0 = time.time()
    
    # Send start event
    if args.jsonl:
        emitter.start(call_id, args.task_id, args.agent_name, args.user_input)
    else:
        print("\n" + "="*100)
        print("🚀 MLA V3 - Multi-Level Agent System")
        print("="*100)
        print(f"📋 Task ID: {args.task_id}")
        print(f"🎛️  Agent System: {args.agent_system}")
        print(f"🤖 Starting Agent: {args.agent_name}")
        print(f"📝 User Input: {args.user_input}")
        print("="*100 + "\n")
    
    try:
        # Initialize configuration loader
        if args.jsonl:
            emitter.token("Loading configuration...")
        else:
            print("📦 Loading configuration...")
        
        config_loader = ConfigLoader(args.agent_system)
        
        if args.jsonl:
            emitter.token(f"Configuration loaded successfully, {len(config_loader.all_tools)} tools/Agents total")
            emitter.progress("init", 10)
        else:
            print(f"✅ Configuration loaded successfully, {len(config_loader.all_tools)} tools/Agents total")
        
        # Initialize hierarchy manager
        if not args.jsonl:
            print("\n📊 Initializing hierarchy manager...")
        hierarchy_manager = get_hierarchy_manager(args.task_id)
        if not args.jsonl:
            print("✅ Hierarchy manager initialized successfully")
        
        # Clean state before starting
        if not args.jsonl:
            print("\n🧹 Checking and cleaning state...")
        
        # If --force-new specified, clear all state
        if args.force_new:
            if not args.jsonl:
                print("🗑️  --force-new: Clearing all state, starting new task")
            context = hierarchy_manager._load_context()
            context["current"] = {
                "instructions": [],
                "hierarchy": {},
                "agents_status": {}
            }
            hierarchy_manager._save_context(context)
            hierarchy_manager._save_stack([])
        else:
            from core.state_cleaner import clean_before_start
            clean_before_start(args.task_id, args.user_input)
        
        # Register user instruction
        if not args.jsonl:
            print(f"\n📝 Registering user instruction...")
        instruction_id = hierarchy_manager.start_new_instruction(args.user_input)
        if not args.jsonl:
            print(f"✅ Instruction registered: {instruction_id}")
        
        # Get Agent configuration
        if not args.jsonl:
            print(f"\n🔍 Finding Agent configuration: {args.agent_name}")
        agent_config = config_loader.get_tool_config(args.agent_name)
        
        if agent_config.get("type") != "llm_call_agent":
            error_msg = f"❌ Error: {args.agent_name} is not an LLM Agent"
            if args.jsonl:
                emitter.error(error_msg)
            else:
                print(error_msg)
            return
        
        if not args.jsonl:
            print(f"✅ Agent configuration loaded successfully")
            print(f"   - Level: {agent_config.get('level', 'unknown')}")
            print(f"   - Model: {agent_config.get('model_type', 'unknown')}")
            print(f"   - Tools: {len(agent_config.get('available_tools', []))}")
            
            # Create and run Agent
            print(f"\n{'='*100}")
            print("▶️  Starting task execution")
            print(f"{'='*100}\n")
        
        agent = AgentExecutor(
            agent_name=args.agent_name,
            agent_config=agent_config,
            config_loader=config_loader,
            hierarchy_manager=hierarchy_manager
        )
        
        # Set tool execution permission mode
        if args.auto_mode is not None:
            auto_mode = args.auto_mode == 'true'
            agent.tool_executor.set_task_permission(args.task_id, auto_mode)
        
        result = agent.run(args.task_id, args.user_input)
        
        # Output result
        if args.jsonl:
            # JSONL mode - send result and end events (full output)
            ok = result.get('status') == 'success'
            summary = result.get('output', '')  # Don't truncate
            emitter.result(ok, summary)
            emitter.end("ok" if ok else "error")
        else:
            # Normal mode
            print(f"\n{'='*100}")
            print("📊 Execution result")
            print(f"{'='*100}")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Output: {result.get('output', 'N/A')}")
            if result.get('error_information'):
                print(f"Error information: {result.get('error_information')}")
            print(f"{'='*100}\n")
        
        # Return status code
        if result.get('status') == 'success':
            return 0
        else:
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted execution")
        return 130
    
    except Exception as e:
        if args.jsonl:
            emitter.error(str(e))
            emitter.end("error")
        else:
            print(f"\n\n❌ Execution failed: {e}")
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
