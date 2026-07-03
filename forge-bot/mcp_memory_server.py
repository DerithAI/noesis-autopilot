#!/usr/bin/env python3
"""
MCP Memory Server for EVO-FORGE Ecosystem
==========================================
SQLite-backed memory with semantic search via sentence-transformers.

Run:
    python mcp_memory_server.py

Or via MCP stdio:
    python mcp_memory_server.py --stdio

Tools:
- memory_store: Store a memory entry
- memory_retrieve: Get memory by ID
- memory_search: Semantic search memories
- memory_list: List recent memories
- memory_delete: Delete a memory
"""
import sys
import os
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import TextContent, Tool
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[!] MCP SDK not installed. Run: pip install mcp")

# Embedding imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("[!] sentence-transformers not installed. Semantic search disabled.")

# =============================================================================
# CONFIG
# =============================================================================
MEMORY_DIR = Path.home() / ".evo_forge" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = MEMORY_DIR / "mcp_memory.db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, good enough

# =============================================================================
# DATABASE
# =============================================================================

class MemoryDatabase:
    """SQLite-backed memory store with optional embeddings."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._embedder = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self._embedder = SentenceTransformer(EMBEDDING_MODEL)
            except Exception as e:
                print(f"[!] Embedding model load failed: {e}")
    
    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '',
                    embedding BLOB,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    context TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _generate_id(self, content: str) -> str:
        return hashlib.sha256(f"{content}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
    
    def _get_embedding(self, text: str) -> Optional[bytes]:
        if not self._embedder:
            return None
        try:
            vec = self._embedder.encode(text, convert_to_numpy=True)
            return vec.tobytes()
        except Exception:
            return None
    
    def store(self, content: str, category: str = "general", tags: List[str] = None, metadata: Dict = None) -> str:
        """Store a memory entry. Returns ID."""
        memory_id = self._generate_id(content)
        tags_str = ",".join(tags or [])
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)
        embedding = self._get_embedding(content)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memories (id, content, category, tags, embedding, metadata, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (memory_id, content, category, tags_str, embedding, meta_str, datetime.utcnow().isoformat())
            )
            conn.commit()
        
        return memory_id
    
    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """Retrieve memory by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
            if row:
                return dict(row)
            return None
    
    def search(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search memories. Uses semantic search if embeddings available, else text search."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            if self._embedder and EMBEDDINGS_AVAILABLE:
                # Semantic search
                query_vec = self._embedder.encode(query, convert_to_numpy=True)
                
                rows = conn.execute("SELECT * FROM memories WHERE embedding IS NOT NULL" + 
                                   (" AND category = ?" if category else ""),
                                   (category,) if category else ()).fetchall()
                
                import numpy as np
                results = []
                for row in rows:
                    mem_vec = np.frombuffer(row["embedding"], dtype=np.float32)
                    # Cosine similarity
                    sim = np.dot(query_vec, mem_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(mem_vec))
                    results.append((sim, dict(row)))
                
                results.sort(key=lambda x: x[0], reverse=True)
                return [r[1] for r in results[:limit]]
            else:
                # Text search fallback
                pattern = f"%{query}%"
                sql = "SELECT * FROM memories WHERE content LIKE ?"
                params = [pattern]
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(sql, params).fetchall()
                return [dict(r) for r in rows]
    
    def list_recent(self, category: str = None, limit: int = 10) -> List[Dict]:
        """List recent memories."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            sql = "SELECT * FROM memories"
            params = []
            if category:
                sql += " WHERE category = ?"
                params.append(category)
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory by ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cur.rowcount > 0
    
    def stats(self) -> Dict:
        """Get memory statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            categories = conn.execute("SELECT category, COUNT(*) as cnt FROM memories GROUP BY category").fetchall()
            return {
                "total_memories": total,
                "categories": {c[0]: c[1] for c in categories},
                "embedding_model": EMBEDDING_MODEL if self._embedder else None,
                "db_path": str(self.db_path)
            }

# =============================================================================
# MCP SERVER
# =============================================================================

class MemoryMCPServer:
    """MCP server exposing memory tools."""
    
    def __init__(self):
        self.db = MemoryDatabase()
        self.server = Server("evo-forge-memory")
        self._register_tools()
    
    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="memory_store",
                    description="Store a memory entry in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Memory content to store"},
                            "category": {"type": "string", "default": "general", "description": "Memory category"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the memory"},
                            "metadata": {"type": "object", "description": "Additional metadata"}
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="memory_retrieve",
                    description="Retrieve a memory by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Memory ID"}
                        },
                        "required": ["id"]
                    }
                ),
                Tool(
                    name="memory_search",
                    description="Search memories by query (semantic or text search)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "category": {"type": "string", "description": "Filter by category"},
                            "limit": {"type": "integer", "default": 5, "description": "Max results"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="memory_list",
                    description="List recent memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Filter by category"},
                            "limit": {"type": "integer", "default": 10, "description": "Max results"}
                        }
                    }
                ),
                Tool(
                    name="memory_delete",
                    description="Delete a memory by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Memory ID to delete"}
                        },
                        "required": ["id"]
                    }
                ),
                Tool(
                    name="memory_stats",
                    description="Get memory database statistics",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "memory_store":
                mid = self.db.store(
                    content=arguments["content"],
                    category=arguments.get("category", "general"),
                    tags=arguments.get("tags", []),
                    metadata=arguments.get("metadata", {})
                )
                return [TextContent(type="text", text=f"✅ Stored memory: {mid}")]
            
            elif name == "memory_retrieve":
                mem = self.db.retrieve(arguments["id"])
                if mem:
                    text = f"📋 Memory {mem['id'][:8]}:\n{mem['content']}\n(category: {mem['category']}, tags: {mem['tags']})"
                else:
                    text = "❌ Memory not found"
                return [TextContent(type="text", text=text)]
            
            elif name == "memory_search":
                results = self.db.search(
                    query=arguments["query"],
                    category=arguments.get("category"),
                    limit=arguments.get("limit", 5)
                )
                if not results:
                    return [TextContent(type="text", text="🔍 No memories found.")]
                
                lines = [f"🔍 Found {len(results)} memories:"]
                for r in results:
                    lines.append(f"- [{r['id'][:8]}] {r['content'][:100]}... (cat: {r['category']})")
                return [TextContent(type="text", text="\n".join(lines))]
            
            elif name == "memory_list":
                results = self.db.list_recent(
                    category=arguments.get("category"),
                    limit=arguments.get("limit", 10)
                )
                if not results:
                    return [TextContent(type="text", text="📭 No memories yet.")]
                
                lines = [f"📋 Recent memories ({len(results)}):"]
                for r in results:
                    lines.append(f"- [{r['created_at'][:16]}] {r['content'][:80]}...")
                return [TextContent(type="text", text="\n".join(lines))]
            
            elif name == "memory_delete":
                success = self.db.delete(arguments["id"])
                return [TextContent(type="text", text="✅ Deleted" if success else "❌ Not found")]
            
            elif name == "memory_stats":
                stats = self.db.stats()
                text = f"""📊 Memory Stats:
Total: {stats['total_memories']}
Categories: {json.dumps(stats['categories'], indent=2)}
Model: {stats['embedding_model'] or 'none (text search only)'}
DB: {stats['db_path']}"""
                return [TextContent(type="text", text=text)]
            
            else:
                return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    
    async def run_stdio(self):
        """Run via stdio transport (for MCP clients)."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    def run_direct(self):
        """Run direct CLI for testing."""
        print("🧠 EVO-FORGE Memory Server (direct mode)")
        print(f"   DB: {DB_PATH}")
        print(f"   Embeddings: {'✅' if EMBEDDINGS_AVAILABLE else '❌ (text search only)'}")
        print()
        print("Commands: store, retrieve, search, list, delete, stats, quit")
        
        while True:
            cmd = input("\n> ").strip()
            if cmd == "quit":
                break
            
            parts = cmd.split(maxsplit=1)
            if not parts:
                continue
            
            action, *rest = parts
            arg = rest[0] if rest else ""
            
            if action == "store":
                mid = self.db.store(arg)
                print(f"✅ Stored: {mid}")
            elif action == "retrieve":
                mem = self.db.retrieve(arg)
                print(json.dumps(mem, indent=2, ensure_ascii=False) if mem else "❌ Not found")
            elif action == "search":
                results = self.db.search(arg)
                for r in results:
                    print(f"- [{r['id'][:8]}] {r['content'][:100]}")
            elif action == "list":
                results = self.db.list_recent()
                for r in results:
                    print(f"- {r['content'][:80]}")
            elif action == "delete":
                success = self.db.delete(arg)
                print("✅ Deleted" if success else "❌ Not found")
            elif action == "stats":
                print(json.dumps(self.db.stats(), indent=2))
            else:
                print("Commands: store, retrieve, search, list, delete, stats, quit")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="EVO-FORGE MCP Memory Server")
    parser.add_argument("--stdio", action="store_true", help="Run as MCP stdio server")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    args = parser.parse_args()
    
    if args.install:
        print("📦 Installing dependencies...")
        deps = ["mcp", "sentence-transformers", "numpy"]
        for dep in deps:
            subprocess.run([sys.executable, "-m", "pip", "install", dep])
        print("✅ Done. Run without --install.")
        return
    
    server = MemoryMCPServer()
    
    if args.stdio:
        if not MCP_AVAILABLE:
            print("❌ MCP SDK not available")
            return 1
        print("🧠 MCP Memory Server starting (stdio mode)...", file=sys.stderr)
        asyncio.run(server.run_stdio())
    else:
        server.run_direct()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
