import argparse
import json
import os
import sys
import subprocess
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from pathlib import Path

# Ollama integration
try:
    import requests
except ImportError:
    print("⚠️  requests not installed. Run: pip install requests")
    requests = None


@dataclass
class Personality:
    name: str = "Echo"
    description: str = "A friendly and helpful assistant."
    
    def to_dict(self) -> Dict:
        return asdict(self)


class OllamaClient:
    """Local Ollama LLM client for bot responses."""
    
    def __init__(self, host: str = None, model: str = "qwen2.5:7b"):
        self.host = host or os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
        # Fix Windows binding issue
        if self.host in ("0.0.0.0", "0.0.0.0:11434", "::"):
            self.host = "127.0.0.1:11434"
        if self.host.startswith("http://"):
            self.host = self.host[7:]
        # Add default port if missing
        if ":" not in self.host:
            self.host += ":11434"
        self.base_url = f"http://{self.host}"
        self.model = model
        self._session_history = []
    
    def chat(self, message: str, system_prompt: str = None, stream: bool = False) -> str:
        """Send message to Ollama and return response."""
        if not requests:
            return "⚠️  requests library not available. Install with: pip install requests"
        
        system = system_prompt or f"You are {self.model}. Be helpful and concise."
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                *self._session_history,
                {"role": "user", "content": message}
            ],
            "stream": stream,
            "options": {"temperature": 0.7, "num_predict": 512}
        }
        
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("message", {}).get("content", "No response")
            
            # Update session history
            self._session_history.append({"role": "user", "content": message})
            self._session_history.append({"role": "assistant", "content": reply})
            
            # Keep history manageable (last 10 turns)
            if len(self._session_history) > 20:
                self._session_history = self._session_history[-20:]
            
            return reply
        except Exception as e:
            return f"❌ Ollama error: {str(e)}"
    
    def list_models(self) -> List[str]:
        """List available local models."""
        if not requests:
            return []
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []


class Bot:
    """EVO-FORGE Bot with Ollama brain and tool hooks."""
    
    def __init__(self, config: dict):
        self.config = config
        self.personality = Personality(**config.get('personality_profile', {}))
        self.ollama = OllamaClient(
            host=config.get('ollama_host'),
            model=config.get('ollama_model', 'qwen2.5:7b')
        )
        self.tool_hooks = config.get('tool_hooks', {})
        self.memory = []  # In-memory conversation history
    
    def respond(self, user_input: str) -> str:
        """Process user input using Ollama LLM."""
        system = f"You are {self.personality.name}. {self.personality.description}"
        response = self.ollama.chat(user_input, system_prompt=system)
        self.memory.append({"user": user_input, "bot": response})
        return response
    
    def execute_tool_command(self, tool_name: str, command: str = "") -> str:
        """Execute a tool hook via HTTP or local command."""
        if tool_name not in self.tool_hooks:
            return f"❌ Tool '{tool_name}' not found. Available: {list(self.tool_hooks.keys())}"
        
        hook = self.tool_hooks[tool_name]
        
        # If hook is a URL, try HTTP
        if hook.startswith("http://") or hook.startswith("https://"):
            if not requests:
                return "❌ requests not installed"
            try:
                resp = requests.post(hook, json={"command": command}, timeout=10)
                return f"✅ {tool_name}: {resp.status_code} | {resp.text[:200]}"
            except Exception as e:
                return f"❌ {tool_name} HTTP error: {str(e)}"
        
        # If hook is a command, run it
        try:
            import shlex
            cmd_parts = hook.split() + shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                capture_output=True, text=True, timeout=30
            )
            output = (result.stdout + result.stderr).strip()[:500]
            return f"✅ {tool_name}: {output}"
        except Exception as e:
            return f"❌ {tool_name} exec error: {str(e)}"
    
    def set_personality(self, name: str, description: str) -> None:
        self.personality.name = name
        self.personality.description = description
        print(f"🎭 Personality set to: {name}")
    
    def get_status(self) -> Dict:
        return {
            "name": self.personality.name,
            "model": self.ollama.model,
            "available_models": self.ollama.list_models(),
            "tools": list(self.tool_hooks.keys()),
            "memory_turns": len(self.memory)
        }


def main():
    parser = argparse.ArgumentParser(
        description="🤖 EVO-FORGE Bot - Local AI assistant with Ollama brain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bot.py chat "What is Python?"
  python bot.py --model deepseek-r1:latest chat "Explain quantum computing"
  python bot.py set-personality "Einstein" "A genius physicist"
  python bot.py status
  python bot.py tool calendar "list events"
        """
    )
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama model to use")
    parser.add_argument("--host", default=None, help="Ollama host (default: 127.0.0.1:11434)")
    sub = parser.add_subparsers(dest="command", help="Command to run")
    
    # chat
    chat_cmd = sub.add_parser("chat", help="Chat with the bot")
    chat_cmd.add_argument("message", nargs="+", help="Message to send")
    
    # set-personality
    pers_cmd = sub.add_parser("set-personality", help="Set bot personality")
    pers_cmd.add_argument("name", help="Personality name")
    pers_cmd.add_argument("description", nargs="+", help="Personality description")
    
    # status
    sub.add_parser("status", help="Show bot status")
    
    # tool
    tool_cmd = sub.add_parser("tool", help="Execute a tool hook")
    tool_cmd.add_argument("tool_name", help="Tool name")
    tool_cmd.add_argument("tool_cmd_str", nargs="?", default="", help="Command to send")
    
    # interactive
    sub.add_parser("interactive", help="Run interactive chat session")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Default config
    config = {
        "ollama_host": args.host,
        "ollama_model": args.model,
        "tool_hooks": {
            "calendar": "http://localhost:8000/calendar",
            "email_client": "http://localhost:8000/email",
            "forge": "python C:\\Users\\Main\\.claude\\skills\\skill-forge\\forge.py",
            "wolf": "python C:\\Users\\Main\\OLLAMA_HERMES\\forge-bot\\wolf_bridge.py" if Path("C:\\Users\\Main\\WOLF_AI").exists() else "echo WOLF_AI not installed",
            "impulse": "python C:\\Users\\Main\\OLLAMA_HERMES\\forge-bot\\impulse_bridge.py" if (Path(__file__).parent / "impulse_bridge.py").exists() else "echo IMPULSE not installed"
        },
        "personality_profile": {
            "name": "EVO-Bot",
            "description": "An adaptive AI assistant built by EVO-FORGE v4.0."
        }
    }
    
    bot = Bot(config)
    
    if args.command == "chat":
        message = " ".join(args.message)
        print(f"🧠 You: {message}")
        reply = bot.respond(message)
        print(f"🤖 {bot.personality.name}: {reply}")
    
    elif args.command == "set-personality":
        desc = " ".join(args.description) if args.description else ""
        bot.set_personality(args.name, desc)
    
    elif args.command == "status":
        status = bot.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.command == "tool":
        result = bot.execute_tool_command(args.tool_name, args.tool_cmd_str)
        print(result)
    
    elif args.command == "interactive":
        print("🤖 EVO-Bot Interactive Mode (type 'exit' to quit)")
        print(f"   Model: {bot.ollama.model} | Host: {bot.ollama.base_url}")
        print("-" * 50)
        while True:
            try:
                user_input = input("🧠 You: ").strip()
                if user_input.lower() in ("exit", "quit", "q"):
                    print("👋 Goodbye!")
                    break
                if not user_input:
                    continue
                reply = bot.respond(user_input)
                print(f"🤖 {bot.personality.name}: {reply}")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break


if __name__ == "__main__":
    main()
