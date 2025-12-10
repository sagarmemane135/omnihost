"""
OmniHost Configuration Module
Handles user preferences like default server, output mode, etc.
"""

import json
from pathlib import Path
from typing import Optional, Dict

CONFIG_DIR = Path.home() / ".omnihost"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure config directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(mode=0o755, parents=True)


def load_config() -> Dict:
    """Load configuration from file."""
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        return {
            "default_server": None,
            "output_mode": "normal",  # normal, compact, silent
            "parallel_connections": 5,
            "timeout": 30,
            "groups": {},  # group_name: [server1, server2, ...]
            "server_tags": {},  # server_name: [tag1, tag2, ...]
            "command_aliases": {},  # alias_name: command_string
            "audit_enabled": True
        }
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure new keys exist for backward compatibility
            if "groups" not in config:
                config["groups"] = {}
            if "server_tags" not in config:
                config["server_tags"] = {}
            if "command_aliases" not in config:
                config["command_aliases"] = {}
            if "audit_enabled" not in config:
                config["audit_enabled"] = True
            return config
    except Exception:
        return {}


def save_config(config: Dict):
    """Save configuration to file."""
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_default_server() -> Optional[str]:
    """Get the default server."""
    config = load_config()
    return config.get("default_server")


def set_default_server(server: str):
    """Set the default server."""
    config = load_config()
    config["default_server"] = server
    save_config(config)


def get_output_mode() -> str:
    """Get output mode preference."""
    config = load_config()
    return config.get("output_mode", "normal")


def set_output_mode(mode: str):
    """Set output mode preference."""
    config = load_config()
    config["output_mode"] = mode
    save_config(config)


def get_server_alias(alias: str) -> Optional[str]:
    """Get actual server name from alias."""
    config = load_config()
    aliases = config.get("aliases", {})
    return aliases.get(alias)


def set_server_alias(alias: str, server: str):
    """Set a server alias."""
    config = load_config()
    if "aliases" not in config:
        config["aliases"] = {}
    config["aliases"][alias] = server
    save_config(config)


def resolve_server(server_input: Optional[str]) -> Optional[str]:
    """
    Resolve server input to actual server name.
    Checks: direct name -> alias -> default server
    """
    if server_input:
        # Check if it's an alias
        alias_result = get_server_alias(server_input)
        if alias_result:
            return alias_result
        return server_input
    
    # No input, try default server
    return get_default_server()


# ========== Group Management ==========

def get_groups() -> Dict:
    """Get all groups."""
    config = load_config()
    return config.get("groups", {})


def get_group_servers(group_name: str) -> list:
    """Get servers in a group."""
    groups = get_groups()
    return groups.get(group_name, [])


def add_group(group_name: str, servers: list):
    """Create or update a group."""
    config = load_config()
    if "groups" not in config:
        config["groups"] = {}
    config["groups"][group_name] = servers
    save_config(config)


def remove_group(group_name: str):
    """Remove a group."""
    config = load_config()
    if "groups" in config and group_name in config["groups"]:
        del config["groups"][group_name]
        save_config(config)


def add_server_to_group(group_name: str, server: str):
    """Add a server to a group."""
    config = load_config()
    if "groups" not in config:
        config["groups"] = {}
    if group_name not in config["groups"]:
        config["groups"][group_name] = []
    if server not in config["groups"][group_name]:
        config["groups"][group_name].append(server)
    save_config(config)


def remove_server_from_group(group_name: str, server: str):
    """Remove a server from a group."""
    config = load_config()
    if "groups" in config and group_name in config["groups"]:
        if server in config["groups"][group_name]:
            config["groups"][group_name].remove(server)
            save_config(config)


# ========== Tag Management ==========

def get_server_tags(server: str) -> list:
    """Get tags for a server."""
    config = load_config()
    server_tags = config.get("server_tags", {})
    return server_tags.get(server, [])


def add_tag_to_server(server: str, tag: str):
    """Add a tag to a server."""
    config = load_config()
    if "server_tags" not in config:
        config["server_tags"] = {}
    if server not in config["server_tags"]:
        config["server_tags"][server] = []
    if tag not in config["server_tags"][server]:
        config["server_tags"][server].append(tag)
    save_config(config)


def remove_tag_from_server(server: str, tag: str):
    """Remove a tag from a server."""
    config = load_config()
    if "server_tags" in config and server in config["server_tags"]:
        if tag in config["server_tags"][server]:
            config["server_tags"][server].remove(tag)
            save_config(config)


def get_servers_by_tag(tag: str) -> list:
    """Get all servers with a specific tag."""
    config = load_config()
    server_tags = config.get("server_tags", {})
    return [server for server, tags in server_tags.items() if tag in tags]


# ========== Command Aliases ==========

def get_command_aliases() -> Dict:
    """Get all command aliases."""
    config = load_config()
    return config.get("command_aliases", {})


def get_command_alias(alias: str) -> Optional[str]:
    """Get command for an alias."""
    aliases = get_command_aliases()
    return aliases.get(alias)


def add_command_alias(alias: str, command: str):
    """Create or update a command alias."""
    config = load_config()
    if "command_aliases" not in config:
        config["command_aliases"] = {}
    config["command_aliases"][alias] = command
    save_config(config)


def remove_command_alias(alias: str):
    """Remove a command alias."""
    config = load_config()
    if "command_aliases" in config and alias in config["command_aliases"]:
        del config["command_aliases"][alias]
        save_config(config)
