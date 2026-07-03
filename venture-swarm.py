#!/usr/bin/env python3
"""
EVO-VENTURE-SWARM v1.0
======================
Multi-agent pipeline: research → architect → implement (EVO-FORGE) → test → deploy
Integrates AI-Venture-Swarm with EVO-FORGE, WOLF_AI, and NOESIS.

Usage:
    python venture-swarm.py "AI startup idea"
    python venture-swarm.py "discord bot for crypto alerts" --model qwen2.5:7b
    python venture-swarm.py "saas dashboard" --swarm --deploy
"""
import sys
import os
import json
import time
import argparse
import subprocess
import asyncio
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

# =============================================================================
# PATHS & CONFIG
# =============================================================================
ROOT = Path(__file__).parent
FORGE_DIR = Path.home() / ".claude" / "skills" / "skill-forge"
EVO_FORGE = FORGE_DIR / "enhanced" / "evo-forge.py"
WOLF_DIR = Path("C:/Users/Main/WOLF_AI")
VENTURE_VAULT = Path("C:/Users/Main/_VAULT_EXTRACT/AI-Venture-Swarm-GENESIS-V5/AI-Venture-Swarm-GENESIS-V5")
NOESIS_DIR = Path("C:/Users/Main/OLLAMA_HERMES/noesis-autopilot")

# Add vault to path for native agents
if str(VENTURE_VAULT) not in sys.path:
    sys.path.insert(0, str(VENTURE_VAULT))

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
if OLLAMA_HOST in ("0.0.0.0", "0.0.0.0:11434", "::"):
    OLLAMA_HOST = "127.0.0.1:11434"
if ":" not in OLLAMA_HOST:
    OLLAMA_HOST += ":11434"

# =============================================================================
# UTILITIES
# =============================================================================
def log(msg: str, agent: str = "swarm"):
    ts = datetime.now().strftime("%H:%M:%S")
    emoji = {
        "swarm": "🐺", "research": "🔍", "architect": "🏗️",
        "implement": "⚒️", "test": "🧪", "deploy": "🚀",
        "wolf": "🐺", "noesis": "🌌", "evo": "🧠"
    }.get(agent, "📋")
    print(f"[{ts}] {emoji} [{agent.upper()}] {msg}", flush=True)

def ollama_generate(prompt: str, model: str = "qwen2.5:7b", timeout: int = 60, max_tokens: int = 1024) -> str:
    """Call local Ollama for text generation."""
    try:
        import requests
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": max_tokens}
        }
        resp = requests.post(f"http://{OLLAMA_HOST}/api/generate", json=payload, timeout=timeout)
        return resp.json().get("response", "").strip()
    except Exception as e:
        log(f"Ollama error: {e}", "swarm")
        return ""

def ollama_chat(messages: List[Dict], model: str = "qwen2.5:7b", timeout: int = 120) -> str:
    """Call Ollama chat API."""
    try:
        import requests
        payload = {"model": model, "messages": messages, "stream": False, "options": {"temperature": 0.7}}
        resp = requests.post(f"http://{OLLAMA_HOST}/api/chat", json=payload, timeout=timeout)
        return resp.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        log(f"Ollama chat error: {e}", "swarm")
        return ""

# =============================================================================
# AGENTS
# =============================================================================

@dataclass
class VentureResult:
    seed: str
    ideas: List[str]
    architecture: Dict
    generated_files: List[str]
    test_results: Dict
    deploy_ready: bool
    duration_sec: float
    timestamp: str

class ResearchAgent:
    """Agent 1: Research + Idea Generation (fast model)"""
    
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
    
    def research(self, seed: str) -> List[str]:
        log(f"Researching: '{seed}'", "research")
        prompt = (
            f"Generate 3 specific, actionable product ideas for: '{seed}'. "
            "Each idea should be 2-5 words. Reply ONLY with a JSON array of 3 strings. "
            'Example: ["Crypto alert Discord bot", "AI SaaS dashboard", "Smart contract analyzer"]'
        )
        response = ollama_generate(prompt, self.model, timeout=30, max_tokens=256)
        
        # Extract JSON array
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                ideas = json.loads(response[start:end])
                if isinstance(ideas, list) and len(ideas) >= 3:
                    log(f"Generated ideas: {ideas}", "research")
                    return ideas[:3]
        except Exception:
            pass
        
        # Fallback
        fallback = [
            f"{seed} automation tool",
            f"AI-powered {seed} platform",
            f"Smart {seed} assistant"
        ]
        log(f"Using fallback ideas: {fallback}", "research")
        return fallback


class ArchitectAgent:
    """Agent 2: System Architecture Design (balanced model)"""
    
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
    
    def design(self, idea: str) -> Dict:
        log(f"Designing architecture for: '{idea}'", "architect")
        prompt = (
            f"Design a minimal tech stack for: '{idea}'. "
            "Reply ONLY with JSON: {\"product\":\"name\",\"backend\":\"fastapi|flask|express\","
            "\"frontend\":\"react|vue|none\",\"database\":\"sqlite|postgres|mongodb\","
            "\"llm\":\"ollama model\",\"features\":[\"feature1\",\"feature2\"],"
            "\"endpoints\":[\"/api/health\",\"/api/chat\"],\"complexity\":\"low|medium|high\"}"
        )
        response = ollama_generate(prompt, self.model, timeout=60, max_tokens=512)
        
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                arch = json.loads(response[start:end])
                log(f"Architecture: {arch.get('backend', 'unknown')} + {arch.get('frontend', 'none')}", "architect")
                return arch
        except Exception:
            pass
        
        # Fallback
        fallback = {
            "product": idea.replace(" ", "_").lower()[:20],
            "backend": "fastapi",
            "frontend": "react",
            "database": "sqlite",
            "llm": "qwen2.5:7b",
            "features": ["API", "Dashboard", "AI Chat"],
            "endpoints": ["/api/health", "/api/chat"],
            "complexity": "medium"
        }
        log(f"Using fallback architecture", "architect")
        return fallback


class ImplementAgent:
    """Agent 3: Code Generation via EVO-FORGE"""
    
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self.forge_script = FORGE_DIR / "forge.py"
    
    def implement(self, architecture: Dict) -> Dict:
        product = architecture.get("product", "venture")
        complexity = architecture.get("complexity", "medium")
        backend = architecture.get("backend", "fastapi")
        frontend = architecture.get("frontend", "react")
        
        log(f"Implementing: {product} ({backend}+{frontend})", "implement")
        
        results = {}
        
        # Generate backend
        if backend in ("fastapi", "flask"):
            backend_intent = f"{backend} api for {product}"
            log(f"Generating backend: {backend_intent}", "implement")
            results["backend"] = self._run_forge(backend_intent, "python", complexity)
        
        # Generate frontend
        if frontend and frontend != "none":
            frontend_intent = f"{frontend} dashboard for {product}"
            log(f"Generating frontend: {frontend_intent}", "implement")
            results["frontend"] = self._run_forge(frontend_intent, frontend, complexity)
        
        # Generate bot if needed
        if "bot" in product.lower() or "discord" in product.lower() or "telegram" in product.lower():
            bot_intent = f"{product} bot"
            log(f"Generating bot: {bot_intent}", "implement")
            results["bot"] = self._run_forge(bot_intent, "python", complexity)
        
        return results
    
    def _run_forge(self, intent: str, stack: str, complexity: str) -> Dict:
        """Run EVO-FORGE for a single intent."""
        if not self.forge_script.exists():
            log("forge.py not found!", "implement")
            return {"error": "forge.py missing"}
        
        cmd = [
            sys.executable, str(self.forge_script),
            intent,
            "--output", "both",
            "--enhanced",
            "--stack", stack,
            "--complexity", complexity,
            "--model", self.model
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
            # forge.py uses exact intent string for directory name
            out_dir = ROOT / f"forge-{intent}"
            files = []
            if out_dir.exists():
                files = [str(f.relative_to(ROOT)) for f in out_dir.rglob("*") if f.is_file()]
                log(f"Found {len(files)} files in {out_dir.name}", "implement")
            else:
                log(f"Directory not found: {out_dir}", "implement")
            
            return {
                "success": result.returncode == 0 and len(files) > 0,
                "files": files,
                "stdout": result.stdout[-500:],
                "stderr": result.stderr[-200:]
            }
        except subprocess.TimeoutExpired:
            return {"error": "Forge timeout", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}


class TestAgent:
    """Agent 4: Quality Assurance"""
    
    def test(self, generated: Dict) -> Dict:
        log("Running quality checks...", "test")
        results = {"passed": 0, "failed": 0, "details": []}
        
        for component, meta in generated.items():
            if not meta.get("success"):
                results["failed"] += 1
                results["details"].append({"component": component, "status": "FAIL", "reason": "Generation failed"})
                continue
            
            files = meta.get("files", [])
            has_tests = any("test" in f.lower() for f in files)
            has_main = any(f.endswith((".py", ".js", ".tsx")) and "test" not in f.lower() for f in files)
            
            if has_main:
                results["passed"] += 1
                results["details"].append({
                    "component": component,
                    "status": "PASS",
                    "files": len(files),
                    "has_tests": has_tests
                })
            else:
                results["failed"] += 1
                results["details"].append({"component": component, "status": "FAIL", "reason": "No main files"})
        
        log(f"Tests: {results['passed']} passed, {results['failed']} failed", "test")
        return results


class DeployAgent:
    """Agent 5: Deployment Packaging"""
    
    def package(self, architecture: Dict, generated: Dict, product_dir: Path) -> bool:
        log("Packaging for deployment...", "deploy")
        
        dockerfile_content = f"""FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt || true
EXPOSE 8000
CMD ["python", "main.py"]
"""
        
        compose_content = f"""version: '3.8'
services:
  {architecture.get('product', 'app')}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=host.docker.internal:11434
"""
        
        req_content = "fastapi\nuvicorn\nrequests\n"
        
        try:
            product_dir.mkdir(parents=True, exist_ok=True)
            (product_dir / "Dockerfile").write_text(dockerfile_content, encoding="utf-8")
            (product_dir / "docker-compose.yml").write_text(compose_content, encoding="utf-8")
            (product_dir / "requirements.txt").write_text(req_content, encoding="utf-8")
            
            readme = f"""# {architecture.get('product', 'App')}
Generated by EVO-VENTURE-SWARM v1.0

## Stack
- Backend: {architecture.get('backend', 'N/A')}
- Frontend: {architecture.get('frontend', 'N/A')}
- Database: {architecture.get('database', 'N/A')}
- LLM: {architecture.get('llm', 'N/A')}

## Quick Start
```bash
docker-compose up --build
```

## Components
{chr(10).join(f"- {k}: {len(v.get('files', []))} files" for k, v in generated.items())}
"""
            (product_dir / "README.md").write_text(readme, encoding="utf-8")
            
            log(f"Deploy package ready: {product_dir}", "deploy")
            return True
        except Exception as e:
            log(f"Deploy error: {e}", "deploy")
            return False


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class VentureSwarm:
    """Main orchestrator: coordinates 5 agents in sequence."""
    
    def __init__(self, model: str = "qwen2.5:7b", research_model: str = "qwen2.5:3b"):
        self.research = ResearchAgent(research_model)
        self.architect = ArchitectAgent(model)
        self.implement = ImplementAgent(model)
        self.test = TestAgent()
        self.deploy = DeployAgent()
        self.model = model
    
    def run(self, seed: str, swarm_mode: bool = False, deploy: bool = False) -> VentureResult:
        start = time.time()
        log(f"🚀 VENTURE-SWARM START: '{seed}'", "swarm")
        
        # Phase 1: Research
        ideas = self.research.research(seed)
        
        # Phase 2: Architect (use first idea)
        primary_idea = ideas[0]
        architecture = self.architect.design(primary_idea)
        
        # Phase 3: Implement
        generated = self.implement.implement(architecture)
        
        # Phase 4: Test
        test_results = self.test.test(generated)
        
        # Phase 5: Deploy
        deploy_ready = False
        if deploy:
            product_dir = ROOT / "ventures" / architecture.get("product", "venture")
            deploy_ready = self.deploy.package(architecture, generated, product_dir)
        
        # Gather all files
        all_files = []
        for meta in generated.values():
            all_files.extend(meta.get("files", []))
        
        duration = time.time() - start
        
        result = VentureResult(
            seed=seed,
            ideas=ideas,
            architecture=architecture,
            generated_files=all_files,
            test_results=test_results,
            deploy_ready=deploy_ready,
            duration_sec=duration,
            timestamp=datetime.now().isoformat()
        )
        
        # Notify WOLF_AI
        self._notify_wolf(result)
        
        # Log to NOESIS
        self._log_noesis(result)
        
        # Print summary
        self._print_summary(result)
        
        return result
    
    def _notify_wolf(self, result: VentureResult):
        if not WOLF_DIR.exists():
            return
        try:
            wolf_script = ROOT / "forge-bot" / "wolf_bridge.py"
            if wolf_script.exists():
                msg = f"Venture completed: {result.architecture.get('product', 'unknown')} ({len(result.generated_files)} files, {result.duration_sec:.0f}s)"
                subprocess.run(
                    [sys.executable, str(wolf_script), "howl", msg],
                    capture_output=True, timeout=10
                )
        except Exception:
            pass
    
    def _log_noesis(self, result: VentureResult):
        try:
            log_file = ROOT / "evo_forge_events.jsonl"
            entry = {
                "timestamp": result.timestamp,
                "event": "venture_swarm_complete",
                "seed": result.seed,
                "product": result.architecture.get("product"),
                "files": len(result.generated_files),
                "duration_sec": result.duration_sec,
                "tests": result.test_results
            }
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
    
    def _print_summary(self, result: VentureResult):
        print("\n" + "=" * 60)
        print("🐺 VENTURE-SWARM COMPLETE")
        print("=" * 60)
        print(f"Seed: {result.seed}")
        print(f"Product: {result.architecture.get('product', 'N/A')}")
        print(f"Stack: {result.architecture.get('backend', 'N/A')} + {result.architecture.get('frontend', 'N/A')}")
        print(f"Files: {len(result.generated_files)}")
        print(f"Tests: {result.test_results['passed']} passed, {result.test_results['failed']} failed")
        print(f"Duration: {result.duration_sec:.1f}s")
        print(f"Deploy: {'✅ Ready' if result.deploy_ready else '❌ Not packaged'}")
        print("=" * 60)
        
        # Print generated directories
        dirs = set()
        for f in result.generated_files:
            parts = f.split(os.sep)
            if len(parts) > 1:
                dirs.add(parts[0])
        if dirs:
            print("📁 Artifacts:")
            for d in sorted(dirs):
                print(f"   ./{d}/")
        print("=" * 60)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="EVO-VENTURE-SWARM: Multi-agent venture builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python venture-swarm.py "AI crypto bot"
  python venture-swarm.py "saas dashboard" --deploy
  python venture-swarm.py "discord moderation bot" --model deepseek-r1:latest
        """
    )
    parser.add_argument("seed", help="Venture seed idea")
    parser.add_argument("--model", default="qwen2.5:7b", help="Main model for architect/implement")
    parser.add_argument("--research-model", default="qwen2.5:3b", help="Fast model for research")
    parser.add_argument("--deploy", action="store_true", help="Package for deployment")
    parser.add_argument("--swarm", action="store_true", help="Enable full swarm mode")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without generation")
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔮 DRY RUN - Simulating venture swarm...")
        print(f"Seed: {args.seed}")
        print(f"Model: {args.model}")
        print(f"Deploy: {args.deploy}")
        return
    
    swarm = VentureSwarm(model=args.model, research_model=args.research_model)
    result = swarm.run(args.seed, swarm_mode=args.swarm, deploy=args.deploy)
    
    # Save result
    result_file = ROOT / f"venture_{result.architecture.get('product', 'result')}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    log(f"Result saved: {result_file}", "swarm")


if __name__ == "__main__":
    main()
