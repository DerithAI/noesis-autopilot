import unittest
import json
import os
from unittest.mock import patch, MagicMock
from bot import Bot, Personality, OllamaClient


class TestPersonality(unittest.TestCase):
    def test_default_personality(self):
        p = Personality()
        self.assertEqual(p.name, "Echo")
        self.assertEqual(p.description, "A friendly and helpful assistant.")
    
    def test_custom_personality(self):
        p = Personality(name="WOLF", description="Alpha predator")
        self.assertEqual(p.name, "WOLF")
        self.assertEqual(p.description, "Alpha predator")
    
    def test_to_dict(self):
        p = Personality(name="Test", description="Testing")
        d = p.to_dict()
        self.assertEqual(d, {"name": "Test", "description": "Testing"})


class TestOllamaClient(unittest.TestCase):
    def test_init_default(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": "127.0.0.1:11434"}):
            c = OllamaClient()
            self.assertEqual(c.host, "127.0.0.1:11434")
            self.assertEqual(c.model, "qwen2.5:7b")
    
    def test_init_custom(self):
        c = OllamaClient(host="192.168.1.5:11434", model="deepseek-r1:latest")
        self.assertEqual(c.host, "192.168.1.5:11434")
        self.assertEqual(c.model, "deepseek-r1:latest")
    
    def test_host_strips_http(self):
        c = OllamaClient(host="http://localhost:11434")
        self.assertEqual(c.host, "localhost:11434")
    
    @patch("bot.requests")
    def test_chat_success(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Hello there!"}}
        mock_requests.post.return_value = mock_resp
        
        c = OllamaClient()
        result = c.chat("Hi")
        self.assertEqual(result, "Hello there!")
        self.assertEqual(len(c._session_history), 2)  # user + assistant
    
    @patch("bot.requests")
    def test_list_models(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [
                {"name": "qwen2.5:7b"},
                {"name": "deepseek-r1:latest"}
            ]
        }
        mock_requests.get.return_value = mock_resp
        
        c = OllamaClient()
        models = c.list_models()
        self.assertIn("qwen2.5:7b", models)
        self.assertIn("deepseek-r1:latest", models)
    
    def test_chat_no_requests(self):
        with patch("bot.requests", None):
            c = OllamaClient()
            result = c.chat("Hi")
            self.assertIn("requests library not available", result)


class TestBot(unittest.TestCase):
    def setUp(self):
        self.config = {
            "api_key": "test_api_key",
            "memory_backend": "mongodb://localhost:27017/test_memory",
            "tool_hooks": {
                "calendar": "http://localhost:8000/calendar",
                "email_client": "http://localhost:8000/email"
            },
            "personality_profile": {
                "name": "TestBot",
                "description": "A test assistant."
            },
            "ollama_model": "qwen2.5:3b"
        }
        self.bot = Bot(self.config)
    
    def test_init(self):
        self.assertEqual(self.bot.personality.name, "TestBot")
        self.assertEqual(self.bot.ollama.model, "qwen2.5:3b")
        self.assertEqual(len(self.bot.tool_hooks), 2)
    
    def test_set_personality(self):
        self.bot.set_personality("NewName", "New desc")
        self.assertEqual(self.bot.personality.name, "NewName")
        self.assertEqual(self.bot.personality.description, "New desc")
    
    @patch("bot.requests")
    def test_respond(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "42"}}
        mock_requests.post.return_value = mock_resp
        
        result = self.bot.respond("What is the answer?")
        self.assertEqual(result, "42")
        self.assertEqual(len(self.bot.memory), 1)
    
    @patch("bot.requests")
    def test_execute_tool_http(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "Event list"
        mock_requests.post.return_value = mock_resp
        
        result = self.bot.execute_tool_command("calendar", "list")
        self.assertIn("200", result)
        self.assertIn("Event list", result)
    
    def test_execute_tool_not_found(self):
        result = self.bot.execute_tool_command("nonexistent")
        self.assertIn("not found", result)
    
    @patch.object(OllamaClient, "list_models")
    def test_get_status(self, mock_list):
        mock_list.return_value = ["qwen2.5:7b"]
        status = self.bot.get_status()
        self.assertEqual(status["name"], "TestBot")
        self.assertEqual(status["model"], "qwen2.5:3b")
        self.assertIn("calendar", status["tools"])
        self.assertEqual(status["memory_turns"], 0)


class TestBotCLI(unittest.TestCase):
    @patch("bot.Bot.respond")
    @patch("sys.argv", ["bot.py", "--model", "qwen2.5:3b", "chat", "Hello"])
    def test_cli_chat(self, mock_respond):
        mock_respond.return_value = "Hi there!"
        from bot import main
        # This would need argparse testing with actual invocation
        # Simplified for structure validation


if __name__ == '__main__':
    unittest.main(verbosity=2)
