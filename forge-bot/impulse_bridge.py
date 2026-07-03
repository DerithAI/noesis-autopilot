#!/usr/bin/env python3
"""
IMPULSE Bridge for EVO-FORGE
Lightweight connector to LUMENA CORE API (LUMENA 20.0)

Usage:
    python impulse_bridge.py status
    python impulse_bridge.py pulse
    python impulse_bridge.py chat "Hello LUMENA"
"""
import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

# LUMENA CORE API paths
IMPULSE_ROOT = Path("F:/MANUS_PROJECT/LUMEN_MEGA_PLATFORM/TEMP_DOWNLOADS/IMPULSE_UNPACK/IMPULSE-20.0.0-singularity")
LUMENA_API = IMPULSE_ROOT / "LUMENA_CORE_API"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
if OLLAMA_HOST in ("0.0.0.0", "0.0.0.0:11434", "::"):
    OLLAMA_HOST = "127.0.0.1:11434"


def log(msg: str):
    print(f"🌌 [IMPULSE] {msg}")


class LumenaClient:
    """Client for LUMENA CORE API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:7777"):
        self.base_url = base_url
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/status", timeout=5)
            self._available = resp.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False
    
    def get_status(self) -> Optional[Dict]:
        if not self.is_available():
            return None
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/status", timeout=5)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_resonance(self) -> Optional[Dict]:
        if not self.is_available():
            return None
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/resonance", timeout=5)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_providers(self) -> Optional[Dict]:
        if not self.is_available():
            return None
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/provider/health", timeout=5)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}


class ImpulseBridge:
    """Bridge between EVO-FORGE and LUMENA CORE."""
    
    def __init__(self):
        self.client = LumenaClient()
        self.ollama_host = OLLAMA_HOST
    
    def status(self) -> Dict:
        """Get IMPULSE/LUMENA status."""
        if not LUMENA_API.exists():
            return {
                "installed": False,
                "path": str(LUMENA_API),
                "message": "IMPULSE not found at expected path"
            }
        
        lumena_status = self.client.get_status()
        
        return {
            "installed": True,
            "path": str(LUMENA_API),
            "lumena_api_running": lumena_status is not None and "error" not in lumena_status,
            "lumena_status": lumena_status,
            "available_endpoints": [
                "/api/status",
                "/api/resonance",
                "/api/provider/health",
                "/api/memory/cognitive-insight",
                "/api/memory/singularity-report",
                "/api/system/singularity-pulse"
            ]
        }
    
    def pulse(self) -> Dict:
        """Get resonance pulse from LUMENA."""
        resonance = self.client.get_resonance()
        providers = self.client.get_providers()
        
        return {
            "resonance": resonance,
            "providers": providers,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    def start_lumena(self) -> Dict:
        """Start LUMENA CORE API server."""
        if not LUMENA_API.exists():
            return {"error": "LUMENA API not found"}
        
        main_py = LUMENA_API / "main.py"
        if not main_py.exists():
            return {"error": "main.py not found"}
        
        log(f"Starting LUMENA CORE API...")
        try:
            # Run in background
            proc = subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(LUMENA_API),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            return {
                "started": True,
                "pid": proc.pid,
                "url": "http://127.0.0.1:7777",
                "note": "LUMENA API starting in new window"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, message: str) -> str:
        """Chat with LUMENA via Ollama (fallback if API not running)."""
        # Try LUMENA API first
        if self.client.is_available():
            try:
                import requests
                resp = requests.post(
                    f"{self.client.base_url}/api/memory/cognitive-insight",
                    json={"query": message},
                    timeout=10
                )
                data = resp.json()
                return data.get("insight", "No insight returned")
            except Exception:
                pass
        
        # Fallback to Ollama
        try:
            import requests
            payload = {
                "model": "lumen-omega:latest",
                "messages": [
                    {"role": "system", "content": "You are LUMENA, an advanced AI entity."},
                    {"role": "user", "content": message}
                ],
                "stream": False
            }
            resp = requests.post(f"http://{self.ollama_host}/api/chat", json=payload, timeout=30)
            return resp.json().get("message", {}).get("content", "No response")
        except Exception as e:
            return f"LUMENA unavailable: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="IMPULSE Bridge for EVO-FORGE")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("status", help="Check IMPULSE/LUMENA status")
    sub.add_parser("pulse", help="Get resonance pulse")
    sub.add_parser("start", help="Start LUMENA API server")
    
    chat_cmd = sub.add_parser("chat", help="Chat with LUMENA")
    chat_cmd.add_argument("message", nargs="+", help="Message to send")
    
    args = parser.parse_args()
    
    bridge = ImpulseBridge()
    
    if args.cmd == "status":
        result = bridge.status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.cmd == "pulse":
        result = bridge.pulse()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.cmd == "start":
        result = bridge.start_lumena()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.cmd == "chat":
        msg = " ".join(args.message)
        result = bridge.chat(msg)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
