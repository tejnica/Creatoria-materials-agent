import unittest
import requests
import json
import os

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.api_examples_file = "examples/api_examples.py"

    def test_api_examples_existence(self):
        """Test API examples file existence"""
        self.assertTrue(os.path.exists(self.api_examples_file))

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_materials_webhook_parameters(self):
        """Test materials webhook with parameters"""
        data = {
            "query": "pressure_drop < 100 Pa/m",
            "category": "pipes"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertIn("materials", response.json())

    def test_materials_webhook_keywords(self):
        """Test materials webhook with keywords"""
        data = {
            "query": "high temperature resistant",
            "category": "insulation"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertIn("materials", response.json())

    def test_materials_webhook_invalid_request(self):
        """Test materials webhook with invalid request"""
        data = {
            "invalid_field": "value"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 422)

    def test_materials_webhook_invalid_category(self):
        """Test materials webhook with invalid category"""
        data = {
            "query": "pressure_drop < 100 Pa/m",
            "category": "invalid_category"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_materials_webhook_invalid_parameters(self):
        """Test materials webhook with invalid parameters"""
        data = {
            "query": "invalid_parameter < 100",
            "category": "pipes"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_materials_webhook_missing_unit(self):
        """Test materials webhook with missing unit"""
        data = {
            "query": "pressure_drop < 100",
            "category": "pipes"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_materials_webhook_invalid_operator(self):
        """Test materials webhook with invalid operator"""
        data = {
            "query": "pressure_drop invalid_operator 100 Pa/m",
            "category": "pipes"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_materials_webhook_complex_query(self):
        """Test materials webhook with complex query"""
        data = {
            "query": "pressure_drop < 100 Pa/m AND temperature > 300 K",
            "category": "pipes"
        }
        response = requests.post(f"{self.base_url}/materials-webhook", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertIn("materials", response.json())

if __name__ == '__main__':
    unittest.main() 