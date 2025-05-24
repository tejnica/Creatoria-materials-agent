import unittest
from parameter_parser import DataValidator
from creatoria_agent import Material

class TestDataValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DataValidator()

    def test_material_validation(self):
        """Test material data validation"""
        # Valid data
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
        self.assertTrue(self.validator.validate_material(material))

        # Invalid category
        material.category = "invalid_category"
        self.assertFalse(self.validator.validate_material(material))

        # Missing required properties
        material.category = "metals"
        material.properties.pop("pressure_drop")
        self.assertFalse(self.validator.validate_material(material))

        # Invalid property values
        material.properties["pressure_drop"] = -50
        self.assertFalse(self.validator.validate_material(material))

    def test_property_validation(self):
        """Test property value validation"""
        # Pressure drop
        self.assertTrue(self.validator.validate_pressure_drop(50))
        self.assertTrue(self.validator.validate_pressure_drop(0))
        self.assertFalse(self.validator.validate_pressure_drop(-50))
        self.assertFalse(self.validator.validate_pressure_drop("invalid"))

        # Temperature
        self.assertTrue(self.validator.validate_temperature(350))
        self.assertTrue(self.validator.validate_temperature(0))
        self.assertFalse(self.validator.validate_temperature(-50))
        self.assertFalse(self.validator.validate_temperature("invalid"))

        # Mass
        self.assertTrue(self.validator.validate_mass(500))
        self.assertTrue(self.validator.validate_mass(0))
        self.assertFalse(self.validator.validate_mass(-500))
        self.assertFalse(self.validator.validate_mass("invalid"))

        # Cost
        self.assertTrue(self.validator.validate_cost(2500))
        self.assertTrue(self.validator.validate_cost(0))
        self.assertFalse(self.validator.validate_cost(-2500))
        self.assertFalse(self.validator.validate_cost("invalid"))

    def test_category_validation(self):
        """Test category validation"""
        # Valid categories
        self.assertTrue(self.validator.validate_category("metals"))
        self.assertTrue(self.validator.validate_category("composites"))
        self.assertTrue(self.validator.validate_category("ceramics"))
        self.assertTrue(self.validator.validate_category("polymers"))
        self.assertTrue(self.validator.validate_category("nanomaterials"))

        # Invalid categories
        self.assertFalse(self.validator.validate_category("invalid_category"))
        self.assertFalse(self.validator.validate_category(""))
        self.assertFalse(self.validator.validate_category(None))

    def test_query_validation(self):
        """Test query validation"""
        # Valid queries
        self.assertTrue(self.validator.validate_query("pressure_drop < 100 Pa/m"))
        self.assertTrue(self.validator.validate_query("inlet_temperature > 300 K"))
        self.assertTrue(self.validator.validate_query("mass < 1000 kg"))
        self.assertTrue(self.validator.validate_query("cost < 5000 USD"))
        self.assertTrue(self.validator.validate_query(
            "pressure_drop < 100 Pa/m AND inlet_temperature > 300 K AND mass < 1000 kg AND cost < 5000 USD"
        ))

        # Invalid queries
        self.assertFalse(self.validator.validate_query(""))
        self.assertFalse(self.validator.validate_query("invalid query"))
        self.assertFalse(self.validator.validate_query("pressure_drop < invalid"))
        self.assertFalse(self.validator.validate_query("pressure_drop < 100"))
        self.assertFalse(self.validator.validate_query("pressure_drop invalid 100 Pa/m"))

    def test_constraint_validation(self):
        """Test constraint validation"""
        # Valid constraints
        constraints = [
            {"parameter": "pressure_drop", "operator": "<", "value": 100, "unit": "Pa/m"},
            {"parameter": "inlet_temperature", "operator": ">", "value": 300, "unit": "K"},
            {"parameter": "mass", "operator": "<", "value": 1000, "unit": "kg"},
            {"parameter": "cost", "operator": "<", "value": 5000, "unit": "USD"}
        ]
        self.assertTrue(self.validator.validate_constraints(constraints))

        # Invalid constraints
        invalid_constraints = [
            {"parameter": "invalid", "operator": "<", "value": 100, "unit": "Pa/m"},
            {"parameter": "pressure_drop", "operator": "invalid", "value": 100, "unit": "Pa/m"},
            {"parameter": "pressure_drop", "operator": "<", "value": "invalid", "unit": "Pa/m"},
            {"parameter": "pressure_drop", "operator": "<", "value": 100, "unit": "invalid"}
        ]
        self.assertFalse(self.validator.validate_constraints(invalid_constraints))

    def test_operator_validation(self):
        """Test operator validation"""
        # Valid operators
        self.assertTrue(self.validator.validate_operator("<"))
        self.assertTrue(self.validator.validate_operator(">"))
        self.assertTrue(self.validator.validate_operator("<="))
        self.assertTrue(self.validator.validate_operator(">="))
        self.assertTrue(self.validator.validate_operator("=="))
        self.assertTrue(self.validator.validate_operator("!="))

        # Invalid operators
        self.assertFalse(self.validator.validate_operator(""))
        self.assertFalse(self.validator.validate_operator("invalid"))
        self.assertFalse(self.validator.validate_operator(None))

if __name__ == '__main__':
    unittest.main() 