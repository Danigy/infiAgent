#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation History Storage - Simplified Version
Only saves action_history, does not save traditional user/assistant dialogues
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ConversationStorage:
    """Conversation history storage"""
    
    def __init__(self, task_id: str = None):
        """Initialize storage - uses user home directory (cross-platform)"""
        self.conversations_dir = Path.home() / "mla_v3" / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.task_id = task_id
    
    def _generate_filename(self, task_id: str, agent_id: str) -> str:
        """Generate conversation filename: hash + last folder name + agent_id"""
        from pathlib import Path
        import hashlib
        
        task_hash = hashlib.md5(task_id.encode()).hexdigest()[:8]
        # Cross-platform path handling: check if it's a path (contains / or \)
        import os
        task_folder = Path(task_id).name if (os.sep in task_id or '/' in task_id or '\\' in task_id) else task_id
        task_name = f"{task_hash}_{task_folder}"
        
        return str(self.conversations_dir / f"{task_name}_{agent_id}_actions.json")
    
    def save_actions(self, task_id: str, agent_id: str, agent_name: str, 
                    task_input: str, action_history: List[Dict], current_turn: int,
                    latest_thinking: str = "", first_thinking_done: bool = False,
                    tool_call_counter: int = 0, system_prompt: str = "",
                    action_history_fact: List[Dict] = None,
                    pending_tools: List[Dict] = None):
        """
        Save action history and complete state
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            agent_name: Agent name
            task_input: Task input
            action_history: Action history list
            current_turn: Current turn number
            latest_thinking: Latest thinking content
            first_thinking_done: Whether first thinking is completed
            tool_call_counter: Tool call counter
            system_prompt: Complete system_prompt (including XML context)
        """
        try:
            filepath = self._generate_filename(task_id, agent_id)
            
            data = {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "task_input": task_input,
                "current_turn": current_turn,
                "action_history": action_history,  # For rendering (will be compressed)
                "action_history_fact": action_history_fact if action_history_fact else action_history,  # Complete trajectory
                "pending_tools": pending_tools if pending_tools else [],  # Pending tools
                "latest_thinking": latest_thinking,
                "first_thinking_done": first_thinking_done,
                "tool_call_counter": tool_call_counter,
                "system_prompt": system_prompt,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # print(f"💾 State saved: Turn {current_turn}, {len(action_history)} actions")
        
        except Exception as e:
            print(f"⚠️ Failed to save conversation history: {e}")
    
    def load_actions(self, task_id: str, agent_id: str) -> Dict:
        """
        Load action history
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            Action history data, or None if not exist
        """
        try:
            filepath = self._generate_filename(task_id, agent_id)
            
            if not Path(filepath).exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📂 Action history loaded: Turn {data.get('current_turn', 0)}, {len(data.get('action_history', []))} actions")
            return data
        
        except Exception as e:
            print(f"⚠️ Failed to load conversation history: {e}")
            return None


if __name__ == "__main__":
    # Test storage
    storage = ConversationStorage()
    
    # Test save
    storage.save_actions(
        task_id="test",
        agent_id="agent_123",
        agent_name="test_agent",
        task_input="Test task",
        action_history=[
            {"tool_name": "file_read", "arguments": {}, "result": {}}
        ],
        current_turn=1
    )
    
    # Test load
    data = storage.load_actions("test", "agent_123")
    print(f"✅ Loaded data: {data}")
