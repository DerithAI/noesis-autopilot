#!/usr/bin/env python3
"""
EVO-Bot Telegram Interface
Lightweight Telegram bot that uses forge-bot's brain.

Setup:
    1. Talk to @BotFather on Telegram
    2. Create bot: /newbot
    3. Set TELEGRAM_BOT_TOKEN in environment
    4. Run: python telegram_bot.py

Commands:
    /start - Welcome
    /chat <msg> - Chat with EVO-Bot via Ollama
    /status - Show bot status
    /wolf <cmd> - Execute WOLF command
    /help - Show help
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add forge-bot to path
FORGE_BOT_DIR = Path(__file__).parent
sys.path.insert(0, str(FORGE_BOT_DIR))

from bot import Bot, OllamaClient

# Telegram imports
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[!] python-telegram-bot not installed. Run: pip install python-telegram-bot")


class ForgeTelegramBot:
    """Telegram interface for EVO-FORGE Bot."""
    
    def __init__(self, token: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot required")
        
        self.token = token
        self.app = None
        
        # Initialize EVO-Bot brain
        self.config = {
            "ollama_model": os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
            "tool_hooks": {
                "wolf": f"python {FORGE_BOT_DIR / 'wolf_bridge.py'}" if (FORGE_BOT_DIR / 'wolf_bridge.py').exists() else "echo wolf not installed",
                "impulse": f"python {FORGE_BOT_DIR / 'impulse_bridge.py'}" if (FORGE_BOT_DIR / 'impulse_bridge.py').exists() else "echo impulse not installed",
            },
            "personality_profile": {
                "name": "EVO-Telegram",
                "description": "AI assistant on Telegram, powered by EVO-FORGE v4.0."
            }
        }
        self.brain = Bot(self.config)
    
    def _is_authorized(self, user_id: int) -> bool:
        allowed = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
        if not allowed:
            return True
        return str(user_id) in allowed.split(",")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not self._is_authorized(user.id):
            await update.message.reply_text(f"Access denied. Your ID: {user.id}")
            return
        
        welcome = f"""
🤖 *EVO-BOT on Telegram*

Welcome, {user.first_name}!

*Commands:*
/chat <msg> - Talk with AI
/status - Bot status
/wolf <cmd> - WOLF_AI bridge
/impulse <cmd> - LUMENA bridge
/help - This message

*Model:* {self.brain.ollama.model}
*Personality:* {self.brain.personality.name}
        """
        await update.message.reply_text(welcome, parse_mode="Markdown")
    
    async def chat_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /chat <your message>")
            return
        
        message = " ".join(context.args)
        await update.message.reply_text("🧠 Thinking...")
        
        try:
            reply = self.brain.respond(message)
            # Escape markdown special chars
            reply = reply.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
            if len(reply) > 4000:
                reply = reply[:4000] + "..."
            await update.message.reply_text(reply, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def status_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        
        status = self.brain.get_status()
        msg = f"""
🤖 *EVO-Bot Status*

*Name:* {status['name']}
*Model:* {status['model']}
*Memory turns:* {status['memory_turns']}
*Available models:* {len(status['available_models'])}
*Tools:* {', '.join(status['tools'])}
        """
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    async def wolf_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /wolf <command>\nExample: /wolf status")
            return
        
        cmd = " ".join(context.args)
        await update.message.reply_text("🐺 Executing...")
        
        try:
            result = self.brain.execute_tool_command("wolf", cmd)
            if len(result) > 4000:
                result = result[:4000] + "..."
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def impulse_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /impulse <command>\nExample: /impulse status")
            return
        
        cmd = " ".join(context.args)
        await update.message.reply_text("🌌 Querying LUMENA...")
        
        try:
            result = self.brain.execute_tool_command("impulse", cmd)
            if len(result) > 4000:
                result = result[:4000] + "..."
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plain text messages as chat."""
        if not self._is_authorized(update.effective_user.id):
            return
        
        message = update.message.text
        
        try:
            reply = self.brain.respond(message)
            reply = reply.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
            if len(reply) > 4000:
                reply = reply[:4000] + "..."
            await update.message.reply_text(reply, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def run(self):
        print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 EVO-BOT Telegram Interface                           ║
    ║   ═══════════════════════════════════════                 ║
    ║                                                           ║
    ║   Bot is running. Send /start to your bot!              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
        """)
        
        self.app = Application.builder().token(self.token).build()
        
        # Handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.start))
        self.app.add_handler(CommandHandler("chat", self.chat_cmd))
        self.app.add_handler(CommandHandler("status", self.status_cmd))
        self.app.add_handler(CommandHandler("wolf", self.wolf_cmd))
        self.app.add_handler(CommandHandler("impulse", self.impulse_cmd))
        
        # Plain messages
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.message_handler
        ))
        
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[!] Set TELEGRAM_BOT_TOKEN environment variable")
        print("    1. Talk to @BotFather on Telegram")
        print("    2. Create bot: /newbot")
        print("    3. Set token: $env:TELEGRAM_BOT_TOKEN='your_token'")
        return 1
    
    bot = ForgeTelegramBot(token)
    bot.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
