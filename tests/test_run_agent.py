import unittest
from fastapi.testclient import TestClient
from run_agent import app
from unittest.mock import patch

class TestRunAgent(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch('run_agent.agent')
    def test_materials_webhook_parameters(self, mock_agent):
        # Настраиваем мок
        mock_agent.search_by_parameters.return_value = [
            {
                "name": "Test Material",
                "category": "metals",
                "properties": {
                    "pressure_drop": 50,
                    "inlet_temperature": 350,
                    "mass": 500,
                    "cost": 2500
                }
            }
        ]

        # Тестируем запрос с параметрами
        data = {
            "query": "pressure_drop < 100 Pa/m AND inlet_temperature > 300 K",
            "category": "metals"
        }
        
        response = self.client.post("/materials-webhook", json=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(len(response.json()["materials"]), 1)
        self.assertEqual(response.json()["materials"][0]["name"], "Test Material")

    @patch('run_agent.agent')
    def test_materials_webhook_keywords(self, mock_agent):
        # Настраиваем мок
        mock_agent.search_by_keywords.return_value = [
            {
                "name": "Test Material",
                "category": "metals",
                "properties": {
                    "pressure_drop": 50,
                    "inlet_temperature": 350,
                    "mass": 500,
                    "cost": 2500
                }
            }
        ]

        # Тестируем запрос с ключевыми словами
        data = {
            "query": "high temperature steel alloy",
            "category": "metals"
        }
        
        response = self.client.post("/materials-webhook", json=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(len(response.json()["materials"]), 1)
        self.assertEqual(response.json()["materials"][0]["name"], "Test Material")

    def test_materials_webhook_invalid_request(self):
        # Тестируем некорректный запрос
        data = {
            "invalid_field": "test"
        }
        
        response = self.client.post("/materials-webhook", json=data)
        
        self.assertEqual(response.status_code, 422)

    @patch('run_agent.agent')
    def test_materials_webhook_error(self, mock_agent):
        # Настраиваем мок для генерации ошибки
        mock_agent.search_by_parameters.side_effect = Exception("Test error")

        # Тестируем запрос, который вызовет ошибку
        data = {
            "query": "pressure_drop < 100 Pa/m",
            "category": "metals"
        }
        
        response = self.client.post("/materials-webhook", json=data)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["error"], "Test error")

if __name__ == '__main__':
    unittest.main() 