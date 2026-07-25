"""
JARVIS — Persistent AI Assistant
Core MONAD cycle adapted for Jarvis.

SEE → THINK → DO → CHECK → REMEMBER → ADAPT
"""
import time
import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

class JarvisCycle:
    """MONAD cycle for Jarvis."""
    
    def __init__(self, seed: Dict, memory=None, voice=None, home=None):
        self.seed = seed
        self.memory = memory
        self.voice = voice
        self.home = home
        self.calm = 0.5  # Initial CALM score
        
    def run_cycle(self, input_signal: str = None) -> Dict:
        """Run one full MONAD cycle."""
        capsule = {
            "id": f"j-{int(time.time())}",
            "time": datetime.now().isoformat(),
            "seed_version": self.seed.get("version", "1.0"),
        }
        
        # SEE — perception
        capsule["signal"] = self._see(input_signal)
        
        # THINK — cognition
        capsule["decision"] = self._think(capsule["signal"])
        
        # DO — action
        capsule["action"] = self._do(capsule["decision"])
        
        # CHECK — evaluation
        capsule["check"] = self._check(capsule["action"], capsule["decision"])
        
        # REMEMBER — save experience
        capsule["remembered"] = self._remember(capsule)
        
        # ADAPT — update seed if needed
        capsule["adapted"] = self._adapt(capsule)
        
        # Update CALM
        self.calm = self._calculate_calm(capsule)
        capsule["calm"] = self.calm
        
        return capsule
    
    def _see(self, input_signal: str = None) -> Dict:
        """Perception — what changed? what needs attention?"""
        signal = {
            "type": "input" if input_signal else "idle",
            "content": input_signal or "no input",
            "timestamp": datetime.now().isoformat(),
            "environment": self._scan_environment(),
            "voice_activity": self.voice.is_listening() if self.voice else False,
        }
        return signal
    
    def _think(self, signal: Dict) -> Dict:
        """Cognition — what does this mean? what should I do?"""
        # Check if input requires action
        if signal["type"] == "idle":
            return {"action": "wait", "reason": "no input, maintaining standby"}
        
        content = signal["content"].lower()
        
        # Simple intent detection (will be replaced with LLM)
        if any(w in content for w in ["turn on", "start", "open"]):
            return {"action": "execute", "target": "device_on", "confidence": 0.8}
        elif any(w in content for w in ["turn off", "stop", "close"]):
            return {"action": "execute", "target": "device_off", "confidence": 0.8}
        elif any(w in content for w in ["what", "tell", "explain"]):
            return {"action": "respond", "target": "answer", "confidence": 0.7}
        else:
            return {"action": "acknowledge", "target": "general", "confidence": 0.5}
    
    def _do(self, decision: Dict) -> Dict:
        """Action — execute the decision."""
        action = decision.get("action", "wait")
        target = decision.get("target", "")
        
        result = {"executed": False, "output": "", "error": None}
        
        if action == "wait":
            result["executed"] = True
            result["output"] = "standby"
        elif action == "execute" and self.home:
            result["executed"] = self.home.execute(target)
            result["output"] = f"Device {target} toggled"
        elif action == "respond" and self.voice:
            response = self._generate_response(target)
            self.voice.speak(response)
            result["executed"] = True
            result["output"] = response
        else:
            result["executed"] = True
            result["output"] = f"Acknowledged: {action}"
        
        return result
    
    def _check(self, action: Dict, decision: Dict) -> Dict:
        """Evaluation — did it work? is seed intact?"""
        check = {
            "success": action.get("executed", False),
            "confidence": decision.get("confidence", 0.5),
            "seed_intact": True,  # Will be validated
            "error": action.get("error"),
        }
        
        # If confidence dropped below threshold, flag for adaptation
        if check["confidence"] < 0.3:
            check["needs_adaptation"] = True
        
        return check
    
    def _remember(self, capsule: Dict) -> bool:
        """Save experience capsule to memory."""
        if self.memory:
            return self.memory.save_capsule(capsule)
        return False
    
    def _adapt(self, capsule: Dict) -> bool:
        """Update seed if check detected issues."""
        check = capsule.get("check", {})
        if check.get("needs_adaptation") or not check.get("success"):
            # Log adaptation need, don't auto-modify seed yet
            self.seed.setdefault("adaptations", []).append({
                "time": datetime.now().isoformat(),
                "reason": check.get("error") or "low confidence",
                "capsule_id": capsule.get("id"),
            })
            return True
        return False
    
    def _calculate_calm(self, capsule: Dict) -> float:
        """CALM = Coherence And Life Metric."""
        check = capsule.get("check", {})
        success = 1.0 if check.get("success") else 0.0
        confidence = check.get("confidence", 0.5)
        seed_intact = 1.0 if check.get("seed_intact") else 0.0
        
        # Weighted average
        calm = (success * 0.4) + (confidence * 0.3) + (seed_intact * 0.3)
        return round(calm, 3)
    
    def _scan_environment(self) -> Dict:
        """Scan home environment for changes."""
        if self.home:
            return self.home.scan()
        return {"status": "no home integration"}
    
    def _generate_response(self, target: str) -> str:
        """Generate a response (will use LLM later)."""
        responses = {
            "answer": "I'm processing your request. Full LLM integration coming soon.",
            "general": "Acknowledged. I'm learning to be more helpful.",
        }
        return responses.get(target, "OK")
