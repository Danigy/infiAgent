!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management Tool
"""

import yaml
import json
from pathlib import Path


def get_config_path(config_name: str = "llm_config") -> Path:
    """Get configuration file path (within package)"""
    # Find package location
    module_path = Path(__file__).parent.parent
    config_file = module_path / "config" / "run_env_config" / f"{config_name}.yaml"
    return config_file


def show_config(config_name: str = "llm_config"):
    """Display configuration"""
    config_file = get_config_path(config_name)
    
    if not config_file.exists():
        print(f"❌ Configuration file does not exist: {config_file}")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"\n📋 Configuration file: {config_file}")
    print(f"{'='*80}")
    print(yaml.dump(config, allow_unicode=True, default_flow_style=False))
    print(f"{'='*80}\n")


def set_config(key: str, value: str, config_name: str = "llm_config"):
    """
    Set configuration item
    
    Args:
        key: Configuration key, supports dot notation (e.g., llm.api_key)
        value: Configuration value
        config_name: Configuration file name
    """
    config_file = get_config_path(config_name)
    
    if not config_file.exists():
        print(f"❌ Configuration file does not exist: {config_file}")
        return
    
    # Read configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
    
    # Parse key path
    keys = key.split('.')
    current = config
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Set value (attempt intelligent type conversion)
    final_key = keys[-1]
    
    # Attempt type conversion
    if value.lower() in ['true', 'false']:
        current[final_key] = value.lower() == 'true'
    elif value.isdigit():
        current[final_key] = int(value)
    elif value.replace('.', '', 1).isdigit():
        current[final_key] = float(value)
    elif value.startswith('[') and value.endswith(']'):
        # List format: attempt to parse as JSON
        try:
            # First try parsing as standard JSON array
            current[final_key] = json.loads(value)
        except json.JSONDecodeError:
            # If fails, handle as simple comma-separated list
            items = value[1:-1].split(',')
            current[final_key] = [item.strip().strip('"').strip("'") for item in items if item.strip()]
    else:
        current[final_key] = value
    
    # Write back configuration
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Configuration updated: {key} = {current[final_key]}")
    print(f"   Configuration file: {config_file}")


def reset_config(config_name: str = "llm_config"):
    """Reset configuration (display path for manual editing)"""
    config_file = get_config_path(config_name)
    print(f"\n📄 Configuration file location: {config_file}")
    print(f"💡 You can directly edit this file, or use:")
    print(f"   mla-agent --config-set KEY VALUE")
    print(f"\nCommon configurations:")
    print(f"   --config-set api_key \"YOUR_KEY\"")
    print(f"   --config-set base_url \"https://api.openai.com/v1\"")
    print(f"   --config-set models \"[gpt-4o,gpt-4o-mini]\"")
    print()


if __name__ == "__main__":
    # Test
    print("View configuration:")
    show_config()
    
    print("\nSet API key:")
    set_config("api_key", "test-key-123")
    
    print("\nView again:")
    show_config()
