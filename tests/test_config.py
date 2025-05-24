import unittest
import json
import os
from pathlib import Path

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_path = Path("config.json")
        self.example_config_path = Path("config.example.json")

    def test_config_exists(self):
        """Проверяем, что конфигурационный файл существует"""
        self.assertTrue(self.config_path.exists())

    def test_example_config_exists(self):
        """Проверяем, что пример конфигурации существует"""
        self.assertTrue(self.example_config_path.exists())

    def test_config_structure(self):
        """Проверяем структуру конфигурационного файла"""
        with open(self.config_path) as f:
            config = json.load(f)

        # Проверяем обязательные поля
        self.assertIn("materials_project", config)
        self.assertIn("aci", config)
        self.assertIn("settings", config)
        self.assertIn("deployment", config)
        self.assertIn("web_search", config)
        self.assertIn("categories", config)
        self.assertIn("logging", config)

        # Проверяем структуру ACI конфигурации
        self.assertIn("api_key", config["aci"])
        self.assertIn("endpoint", config["aci"])
        self.assertIn("agent_id", config["aci"])

        # Проверяем структуру настроек
        self.assertIn("retry_attempts", config["settings"])
        self.assertIn("retry_delay", config["settings"])
        self.assertIn("max_workers", config["settings"])
        self.assertIn("timeout", config["settings"])
        self.assertIn("environment", config["settings"])
        self.assertIn("log_level", config["settings"])

        # Проверяем структуру настроек развертывания
        self.assertIn("host", config["deployment"])
        self.assertIn("port", config["deployment"])
        self.assertIn("workers", config["deployment"])
        self.assertIn("reload", config["deployment"])

        # Проверяем структуру настроек веб-поиска
        self.assertIn("enabled", config["web_search"])
        self.assertIn("sources", config["web_search"])
        self.assertIn("max_results_per_source", config["web_search"])
        self.assertIn("min_confidence", config["web_search"])
        self.assertIn("selenium", config["web_search"])

        # Проверяем структуру категорий
        self.assertIn("composites", config["categories"])
        self.assertIn("ceramics", config["categories"])
        self.assertIn("metals", config["categories"])
        self.assertIn("polymers", config["categories"])
        self.assertIn("nanomaterials", config["categories"])

        # Проверяем структуру настроек логирования
        self.assertIn("level", config["logging"])
        self.assertIn("format", config["logging"])
        self.assertIn("file", config["logging"])
        self.assertIn("cloud_logging", config["logging"])

    def test_config_values(self):
        """Проверяем значения в конфигурационном файле"""
        with open(self.config_path) as f:
            config = json.load(f)

        # Проверяем значения настроек
        self.assertIsInstance(config["settings"]["retry_attempts"], int)
        self.assertIsInstance(config["settings"]["retry_delay"], int)
        self.assertIsInstance(config["settings"]["max_workers"], int)
        self.assertIsInstance(config["settings"]["timeout"], int)
        self.assertIn(config["settings"]["environment"], ["development", "production"])
        self.assertIn(config["settings"]["log_level"], ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

        # Проверяем значения настроек развертывания
        self.assertIsInstance(config["deployment"]["port"], int)
        self.assertIsInstance(config["deployment"]["workers"], int)
        self.assertIsInstance(config["deployment"]["reload"], bool)

        # Проверяем значения настроек веб-поиска
        self.assertIsInstance(config["web_search"]["enabled"], bool)
        self.assertIsInstance(config["web_search"]["max_results_per_source"], int)
        self.assertIsInstance(config["web_search"]["min_confidence"], float)

        # Проверяем значения категорий
        for category in config["categories"].values():
            self.assertIn("description", category)
            self.assertIn("keywords", category)
            self.assertIsInstance(category["keywords"], list)

if __name__ == '__main__':
    unittest.main() 