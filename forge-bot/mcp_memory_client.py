#!/usr/bin/env python3
"""
MCP Memory Client for EVO-Bot
Lightweight client to connect to MCP memory server.

Usage:
    from mcp_memory_client import MCPMemoryClient
    
    mem = MCPMemoryClient()
    mem.store("User prefers dark mode", category="preferences", tags=["ui"])
    results = mem.search("dark mode")
"""
import sys
import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any

# MCP imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPMemoryClient:
    """Client for MCP memory operations."""
    
    def __init__(self, server_script: Path = None):
        self.server_script = server_script or Path(__file__).parent / "mcp_memory_server.py"
        self._session = None
        self._tools = []
    
    def _ensure_server(self) -> bool:
        """Check if server script exists."""
        return self.server_script.exists()
    
    async def _connect(self):
        """Connect to MCP memory server via stdio."""
        if not MCP_AVAILABLE:
            raise ImportError("MCP SDK not installed")
        
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self.server_script), "--stdio"],
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self._session = session
                # List available tools
                tools = await session.list_tools()
                self._tools = [t.name for t in tools.tools]
                return session
    
    def _run_sync(self, coro):
        """Run async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already running (e.g., in Jupyter), use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    def store(self, content: str, category: str = "general", tags: List[str] = None, metadata: Dict = None) -> str:
        """Store a memory entry."""
        if not self._ensure_server():
            return "❌ Server script not found"
        
        async def _store():
            async with self._connect() as session:
                result = await session.call_tool("memory_store", {
                    "content": content,
                    "category": category,
                    "tags": tags or [],
                    "metadata": metadata or {}
                })
                return result.content[0].text
        
        return self._run_sync(_store())
    
    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """Retrieve memory by ID."""
        if not self._ensure_server():
            return None
        
        async def _retrieve():
            async with self._connect() as session:
                result = await session.call_tool("memory_retrieve", {"id": memory_id})
                text = result.content[0].text
                if "❌" not in text:
                    return {"text": text}
                return None
        
        return self._run_sync(_retrieve())
    
    def search(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search memories."""
        if not self._ensure_server():
            return []
        
        async def _search():
            async with self._connect() as session:
                args = {"query": query, "limit": limit}
                if category:
                    args["category"] = category
                result = await session.call_tool("memory_search", args)
                text = result.content[0].text
                # Parse results from text
                lines = text.split("\n")[1:]  # Skip header
                memories = []
                for line in lines:
                    if line.startswith("- ["):
                        # Extract ID and content
                        parts = line.split("] ", 1)
                        if len(parts) == 2:
                            memories.append({"summary": parts[1]})
                return memories
        
        return self._run_sync(_search())
    
    def list_recent(self, category: str = None, limit: int = 10) -> List[Dict]:
        """List recent memories."""
        if not self._ensure_server():
            return []
        
        async def _list():
            async with self._connect() as session:
                args = {"limit": limit}
                if category:
                    args["category"] = category
                result = await session.call_tool("memory_list", args)
                text = result.content[0].text
                lines = text.split("\n")[1:]
                memories = []
                for line in lines:
                    if line.startswith("- "):
                        memories.append({"summary": line[2:]})
                return memories
        
        return self._run_sync(_list())
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory by ID."""
        if not self._ensure_server():
            return False
        
        async def _delete():
            async with self._connect() as session:
                result = await session.call_tool("memory_delete", {"id": memory_id})
                return "✅" in result.content[0].text
        
        return self._run_sync(_delete())
    
    def stats(self) -> Dict:
        """Get memory statistics."""
        if not self._ensure_server():
            return {"error": "Server not found"}
        
        async def _stats():
            async with self._connect() as session:
                result = await session.call_tool("memory_stats", {})
                text = result.content[0].text
                return {"text": text}
        
        return self._run_sync(_stats())


class DirectMemoryClient:
    """Direct client using the database without MCP transport (faster)."""
    
    def __init__(self, db_path: Path = None):
        from mcp_memory_server import MemoryDatabase, DB_PATH
        self.db = MemoryDatabase(db_path or DB_PATH)
    
    def store(self, content: str, category: str = "general", tags: List[str] = None, metadata: Dict = None) -> str:
        return self.db.store(content, category, tags, metadata)
    
    def retrieve(self, memory_id: str) -> Optional[Dict]:
        return self.db.retrieve(memory_id)
    
    def search(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        return self.db.search(query, category, limit)
    
    def list_recent(self, category: str = None, limit: int = 10) -> List[Dict]:
        return self.db.list_recent(category, limit)
    
    def delete(self, memory_id: str) -> bool:
        return self.db.delete(memory_id)
    
    def stats(self) -> Dict:
        return self.db.stats()


# Default client - uses direct mode for simplicity
MemoryClient = DirectMemoryClient


def demo():
    """Quick demo of memory operations."""
    print("🧠 MCP Memory Client Demo\n")
    
    client = MemoryClient()
    
    # Store some memories
    print("Storing memories...")
    m1 = client.store("EVO-FORGE v4.0 released with Venture-Swarm", category="changelog", tags=["release", "evo"])
    m2 = client.store("User prefers dark mode UI", category="preferences", tags=["ui", "settings"])
    m3 = client.store("WOLF_AI pack connected successfully", category="logs", tags=["wolf", "integration"])
    print(f"   Stored: {m1[:8]}, {m2[:8]}, {m3[:8]}\n")
    
    # Search
    print("Searching for 'dark mode'...")
    results = client.search("dark mode")
    for r in results:
        print(f"   - {r['content'][:80]}")
    
    # List
    print("\nRecent memories:")
    recent = client.list_recent(limit=3)
    for r in recent:
        print(f"   - [{r['category']}] {r['content'][:60]}...")
    
    # Stats
    print("\nStats:")
    print(json.dumps(client.stats(), indent=2))


if __name__ == "__main__":
    demo()
