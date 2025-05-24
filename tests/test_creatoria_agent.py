import unittest
from unittest.mock import Mock, patch
from creatoria_agent import MaterialsAgent, Material

class TestMaterialsAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MaterialsAgent()

    def test_material_creation(self):
        material = Material(
            name="Test Material",
            category="metals",
            properties={
                "pressure_drop": 50,
                "inlet_temperature": 350,
                "mass": 500,
                "cost": 2500
            }
        )
        self.assertEqual(material.name, "Test Material")
        self.assertEqual(material.category, "metals")
        self.assertEqual(material.properties["pressure_drop"], 50)
        self.assertEqual(material.properties["inlet_temperature"], 350)
        self.assertEqual(material.properties["mass"], 500)
        self.assertEqual(material.properties["cost"], 2500)

    @patch('creatoria_agent.MaterialsAgent.search_online')
    def test_search_by_parameters(self, mock_search_online):
        # Настраиваем мок
        mock_search_online.return_value = [
            Material(
                name="Test Material 1",
                category="metals",
                properties={
                    "pressure_drop": 50,
                    "inlet_temperature": 350,
                    "mass": 500,
                    "cost": 2500
                }
            ),
            Material(
                name="Test Material 2",
                category="metals",
                properties={
                    "pressure_drop": 80,
                    "inlet_temperature": 400,
                    "mass": 800,
                    "cost": 4000
                }
            )
        ]

        # Тестируем поиск
        query = "pressure_drop < 100 Pa/m AND inlet_temperature > 300 K AND mass < 1000 kg AND cost < 5000 USD"
        results = self.agent.search_by_parameters(query, "metals")

        # Проверяем результаты
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].name, "Test Material 1")
        self.assertEqual(results[1].name, "Test Material 2")

    def test_check_constraints(self):
        material = Material(
            name="Test Material",
            category="metals",
            properties={
                "pressure_drop": 50,
                "inlet_temperature": 350,
                "mass": 500,
                "cost": 2500
            }
        )

        constraints = [
            {"parameter": "pressure_drop", "operator": "<", "value": 100},
            {"parameter": "inlet_temperature", "operator": ">", "value": 300},
            {"parameter": "mass", "operator": "<", "value": 1000},
            {"parameter": "cost", "operator": "<", "value": 5000}
        ]

        self.assertTrue(self.agent.check_constraints(material, constraints))

    def test_check_constraints_failure(self):
        material = Material(
            name="Test Material",
            category="metals",
            properties={
                "pressure_drop": 150,
                "inlet_temperature": 250,
                "mass": 1500,
                "cost": 6000
            }
        )

        constraints = [
            {"parameter": "pressure_drop", "operator": "<", "value": 100},
            {"parameter": "inlet_temperature", "operator": ">", "value": 300},
            {"parameter": "mass", "operator": "<", "value": 1000},
            {"parameter": "cost", "operator": "<", "value": 5000}
        ]

        self.assertFalse(self.agent.check_constraints(material, constraints))

    def test_generate_n8n_json(self):
        materials = [
            Material(
                name="Test Material 1",
                category="metals",
                properties={
                    "pressure_drop": 50,
                    "inlet_temperature": 350,
                    "mass": 500,
                    "cost": 2500
                }
            ),
            Material(
                name="Test Material 2",
                category="metals",
                properties={
                    "pressure_drop": 80,
                    "inlet_temperature": 400,
                    "mass": 800,
                    "cost": 4000
                }
            )
        ]

        json_data = self.agent.generate_n8n_json(materials)
        
        self.assertEqual(json_data["status"], "success")
        self.assertEqual(len(json_data["materials"]), 2)
        self.assertEqual(json_data["materials"][0]["name"], "Test Material 1")
        self.assertEqual(json_data["materials"][1]["name"], "Test Material 2")

if __name__ == '__main__':
    unittest.main() 