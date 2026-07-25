"""
JARVIS Voice — TTS, STT, wake word detection.
Uses Ollama for TTS (if available) or system TTS.
"""
import subprocess
import os
from typing import Optional

class VoiceModule:
    """Voice interface for Jarvis."""
    
    def __init__(self, tts_engine: str = "system", stt_engine: str = "whisper"):
        self.tts_engine = tts_engine
        self.stt_engine = stt_engine
        self.listening = False
    
    def speak(self, text: str) -> bool:
        """Text-to-speech."""
        if self.tts_engine == "system":
            return self._system_tts(text)
        elif self.tts_engine == "ollama":
            return self._ollama_tts(text)
        return False
    
    def listen(self, duration: int = 5) -> Optional[str]:
        """Speech-to-text."""
        self.listening = True
        try:
            if self.stt_engine == "whisper":
                return self._whisper_stt(duration)
            return None
        finally:
            self.listening = False
    
    def is_listening(self) -> bool:
        return self.listening
    
    def _system_tts(self, text: str) -> bool:
        """Use system TTS (Windows)."""
        try:
            # Windows PowerShell TTS
            subprocess.run(
                ["powershell", "-Command", f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"],
                capture_output=True, timeout=10
            )
            return True
        except Exception:
            return False
    
    def _ollama_tts(self, text: str) -> bool:
        """Use Ollama for TTS (if model available)."""
        # Placeholder — Ollama doesn't have native TTS yet
        # Could use external TTS service or wait for Ollama TTS support
        return self._system_tts(text)
    
    def _whisper_stt(self, duration: int) -> Optional[str]:
        """Use Whisper for STT."""
        # Placeholder — requires whisper model and audio recording
        # Would use: whisper.record(duration) → whisper.transcribe()
        return None
