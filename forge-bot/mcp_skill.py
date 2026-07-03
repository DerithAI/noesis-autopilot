#!/usr/bin/env python3
"""
MCP Memory Skill for OpenCode
Integrates MCP memory tools into agent workflows.

Usage in agent prompts:
    Use the memory_store tool to save important insights.
    Use memory_search to recall relevant context.

Or direct Python:
    from forge_bot.mcp_memory_client import MemoryClient
    mem = MemoryClient()
    mem.store("Key insight", category="research")
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import client
try:
    from mcp_memory_client import MemoryClient
    _client = MemoryClient()
    _available = True
except Exception:
    _available = False
    _client = None


def is_available() -> bool:
    return _available


def memory_store(content: str, category: str = "general", tags: List[str] = None) -> str:
    """Store a memory entry. Returns memory ID."""
    if not _available:
        return "Memory system not available"
    return _client.store(content, category, tags or [])


def memory_search(query: str, category: str = None, limit: int = 5) -> List[Dict]:
    """Search memories by query."""
    if not _available:
        return []
    return _client.search(query, category, limit)


def memory_list(category: str = None, limit: int = 10) -> List[Dict]:
    """List recent memories."""
    if not _available:
        return []
    return _client.list_recent(category, limit)


def memory_stats() -> Dict:
    """Get memory statistics."""
    if not _available:
        return {"error": "Memory system not available"}
    return _client.stats()


# Tool definitions for MCP/Agent use
TOOLS = [
    {
        "name": "memory_store",
        "description": "Store a memory entry for later retrieval",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to store"},
                "category": {"type": "string", "default": "general"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["content"]
        }
    },
    {
        "name": "memory_search",
        "description": "Search stored memories by query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "memory_list",
        "description": "List recent memories",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "memory_stats",
        "description": "Get memory database statistics",
        "parameters": {"type": "object", "properties": {}}
    }
]
