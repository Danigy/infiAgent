#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Loader - Reads configuration files from agent_library
"""

import os
import yaml
from typing import Dict, List, Any
from pathlib import Path


class ConfigLoader:
    """Configuration loader responsible for reading and merging agent configurations"""
    
    def __init__(self, agent_system_name: str = "infiHelper"):
        """
        Initialize configuration loader
        
        Args:
            agent_system_name: Agent system name, corresponding to folder under agent_library
        """
        self.agent_system_name = agent_system_name
        
        # Find configuration directory (supports both MLA_V3 and original Multi-Level-Agent)
        self.config_root = self._find_config_root()
        self.agent_config_dir = os.path.join(
            self.config_root, "agent_library", agent_system_name
        )
        
        if not os.path.exists(self.agent_config_dir):
            raise FileNotFoundError(f"Agent configuration directory does not exist: {self.agent_config_dir}")
        
        # Load all configurations
        self.general_prompts = self._load_general_prompts()
        self.all_tools = self._load_all_tools()
        
    def _find_config_root(self) -> str:
        """Find configuration root directory"""
        # Use MLA_V3's own config directory
        current_dir = Path(__file__).parent.parent
        mla_v3_config = current_dir / "config"
        
        if not mla_v3_config.exists():
            raise FileNotFoundError(f"Configuration directory does not exist: {mla_v3_config}")
        
        return str(mla_v3_config)
    
    def _load_general_prompts(self) -> Dict:
        """
        Load general prompt configuration
        
        Note: general_prompts.yaml now uses XML format
        This is read directly by ContextBuilder, this method is kept for compatibility
        """
        prompts_file = os.path.join(self.agent_config_dir, "general_prompts.yaml")
        if not os.path.exists(prompts_file):
            return {}
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            # Compatible with old format
            return data.get("general_prompts", {})
    
    def _load_all_tools(self) -> Dict[str, Dict]:
        """Load all tool and Agent configurations"""
        all_tools = {}
        
        # Find all level configuration files
        for filename in os.listdir(self.agent_config_dir):
            if filename.startswith("level_") and filename.endswith(".yaml"):
                filepath = os.path.join(self.agent_config_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    tools = data.get("tools", {})
                    all_tools.update(tools)
        
        return all_tools
    
    def get_tool_config(self, tool_name: str) -> Dict:
        """
        Get configuration for specified tool, and handle available_tool_level field
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool configuration dictionary
        """
        if tool_name not in self.all_tools:
            raise KeyError(f"Tool {tool_name} does not exist in configuration")
        
        config = self.all_tools[tool_name].copy()
        
        # Handle available_tool_level (special case: judge_agent)
        if "available_tool_level" in config and "available_tools" not in config:
            tool_level = config["available_tool_level"]
            # Get all tools at that level
            level_tools = self.get_available_tools_by_level(tool_level)
            config["available_tools"] = level_tools
            print(f"✅ Automatically generated tool list for {tool_name} (Level {tool_level}): {len(level_tools)} tools")
        
        return config
    
    def build_agent_system_prompt(self, agent_config: Dict) -> str:
        """
        ⚠️ Deprecated: This method is no longer used
        
        Context building has been moved to ContextBuilder.build_context()
        This method is responsible for reading general_prompts.yaml (XML format) and building complete context
        """
        # Keep this method only for backward compatibility
        return ""
    
    def get_available_tools_by_level(self, level: int) -> List[str]:
        """
        Get all tool names for specified level
        
        Args:
            level: Tool level
            
        Returns:
            List of tool names
        """
        tools = []
        for tool_name, tool_config in self.all_tools.items():
            if tool_config.get("level") == level:
                tools.append(tool_name)
        return tools


if __name__ == "__main__":
    # Test configuration loading
    loader = ConfigLoader("infiHelper")
    print(f"✅ Successfully loaded configuration system: {loader.agent_system_name}")
    print(f"📁 Configuration directory: {loader.agent_config_dir}")
    print(f"🔧 Total {len(loader.all_tools)} tools/Agents loaded")
    print(f"\nLevel 0 tools count: {len(loader.get_available_tools_by_level(0))}")
    print(f"Level 1 Agents count: {len(loader.get_available_tools_by_level(1))}")

