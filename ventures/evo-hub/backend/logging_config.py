"""
Structured Logging with Loguru
Phase 2.3: Replace console.log/print with structured logging
"""
import sys
import os
from pathlib import Path
from loguru import logger
from typing import Optional

# Configure loguru
LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Console handler (colored, human-readable)
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# File handler (JSON for machine parsing)
logger.add(
    LOG_DIR / "evo-hub_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | {extra}",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    serialize=True,
)

# Error file handler
logger.add(
    LOG_DIR / "evo-hub_errors_{time:YYYY-MM-DD}.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | {extra} | {exception}",
    rotation="1 day",
    retention="90 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)

class StructuredLogger:
    """Wrapper for consistent structured logging across the app."""
    
    def __init__(self, name: str):
        self.logger = logger.bind(module=name)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(message, **kwargs)
    
    def api_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        self.logger.info(
            "API Request",
            method=method,
            path=path,
            status=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def bridge_call(self, bridge: str, action: str, success: bool, duration_ms: float, **kwargs):
        self.logger.info(
            "Bridge Call",
            bridge=bridge,
            action=action,
            success=success,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def venture_action(self, action: str, venture: str, success: bool, **kwargs):
        self.logger.info(
            "Venture Action",
            action=action,
            venture=venture,
            success=success,
            **kwargs
        )

def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance for a module."""
    return StructuredLogger(name)

# Initialize main logger
main_logger = get_logger("evo-hub")

# Test
if __name__ == "__main__":
    main_logger.info("Logging system initialized", version="1.0")
    main_logger.debug("Debug test", component="logging")
    main_logger.warning("Warning test", threshold=80)
    main_logger.error("Error test", code="E001")
    main_logger.api_request("GET", "/api/ventures", 200, 45.2)
    main_logger.bridge_call("mas", "status", True, 120.5)
    main_logger.venture_action("generate", "test-venture", True)
    
    try:
        raise ValueError("Test exception")
    except Exception:
        main_logger.exception("Caught exception")