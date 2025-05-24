import unittest
from parameter_parser import UnitConverter

class TestUnitConverter(unittest.TestCase):
    def setUp(self):
        self.converter = UnitConverter()

    def test_pressure_drop_conversion(self):
        """Test pressure drop unit conversion"""
        # Pascals per meter
        self.assertEqual(self.converter.convert_pressure_drop(100, "Pa/m", "Pa/m"), 100)
        self.assertEqual(self.converter.convert_pressure_drop(100, "Pa/m", "kPa/m"), 0.1)
        self.assertEqual(self.converter.convert_pressure_drop(100, "Pa/m", "bar/m"), 0.001)
        
        # Kilopascals per meter
        self.assertEqual(self.converter.convert_pressure_drop(1, "kPa/m", "Pa/m"), 1000)
        self.assertEqual(self.converter.convert_pressure_drop(1, "kPa/m", "kPa/m"), 1)
        self.assertEqual(self.converter.convert_pressure_drop(1, "kPa/m", "bar/m"), 0.01)
        
        # Bars per meter
        self.assertEqual(self.converter.convert_pressure_drop(1, "bar/m", "Pa/m"), 100000)
        self.assertEqual(self.converter.convert_pressure_drop(1, "bar/m", "kPa/m"), 100)
        self.assertEqual(self.converter.convert_pressure_drop(1, "bar/m", "bar/m"), 1)

    def test_temperature_conversion(self):
        """Test temperature unit conversion"""
        # Kelvin
        self.assertEqual(self.converter.convert_temperature(300, "K", "K"), 300)
        self.assertEqual(self.converter.convert_temperature(300, "K", "C"), 26.85)
        self.assertEqual(self.converter.convert_temperature(300, "K", "F"), 80.33)
        
        # Celsius
        self.assertEqual(self.converter.convert_temperature(25, "C", "K"), 298.15)
        self.assertEqual(self.converter.convert_temperature(25, "C", "C"), 25)
        self.assertEqual(self.converter.convert_temperature(25, "C", "F"), 77)
        
        # Fahrenheit
        self.assertEqual(self.converter.convert_temperature(80, "F", "K"), 299.82)
        self.assertEqual(self.converter.convert_temperature(80, "F", "C"), 26.67)
        self.assertEqual(self.converter.convert_temperature(80, "F", "F"), 80)

    def test_mass_conversion(self):
        """Test mass unit conversion"""
        # Kilograms
        self.assertEqual(self.converter.convert_mass(1000, "kg", "kg"), 1000)
        self.assertEqual(self.converter.convert_mass(1000, "kg", "g"), 1000000)
        self.assertEqual(self.converter.convert_mass(1000, "kg", "t"), 1)
        
        # Grams
        self.assertEqual(self.converter.convert_mass(1000, "g", "kg"), 1)
        self.assertEqual(self.converter.convert_mass(1000, "g", "g"), 1000)
        self.assertEqual(self.converter.convert_mass(1000, "g", "t"), 0.001)
        
        # Tonnes
        self.assertEqual(self.converter.convert_mass(1, "t", "kg"), 1000)
        self.assertEqual(self.converter.convert_mass(1, "t", "g"), 1000000)
        self.assertEqual(self.converter.convert_mass(1, "t", "t"), 1)

    def test_cost_conversion(self):
        """Test cost unit conversion"""
        # US Dollars
        self.assertEqual(self.converter.convert_cost(1000, "USD", "USD"), 1000)
        self.assertEqual(self.converter.convert_cost(1000, "USD", "EUR"), 850)  # Approximate rate
        self.assertEqual(self.converter.convert_cost(1000, "USD", "RUB"), 75000)  # Approximate rate
        
        # Euros
        self.assertEqual(self.converter.convert_cost(1000, "EUR", "USD"), 1176.47)  # Approximate rate
        self.assertEqual(self.converter.convert_cost(1000, "EUR", "EUR"), 1000)
        self.assertEqual(self.converter.convert_cost(1000, "EUR", "RUB"), 88235.29)  # Approximate rate
        
        # Russian Rubles
        self.assertEqual(self.converter.convert_cost(1000, "RUB", "USD"), 13.33)  # Approximate rate
        self.assertEqual(self.converter.convert_cost(1000, "RUB", "EUR"), 11.33)  # Approximate rate
        self.assertEqual(self.converter.convert_cost(1000, "RUB", "RUB"), 1000)

    def test_invalid_unit_conversion(self):
        """Test invalid unit conversion handling"""
        with self.assertRaises(ValueError):
            self.converter.convert_pressure_drop(100, "invalid", "Pa/m")
        
        with self.assertRaises(ValueError):
            self.converter.convert_temperature(300, "K", "invalid")
        
        with self.assertRaises(ValueError):
            self.converter.convert_mass(1000, "kg", "invalid")
        
        with self.assertRaises(ValueError):
            self.converter.convert_cost(1000, "USD", "invalid")

    def test_unit_validation(self):
        """Test unit validation"""
        # Check pressure drop units
        self.assertTrue(self.converter.is_valid_pressure_drop_unit("Pa/m"))
        self.assertTrue(self.converter.is_valid_pressure_drop_unit("kPa/m"))
        self.assertTrue(self.converter.is_valid_pressure_drop_unit("bar/m"))
        self.assertFalse(self.converter.is_valid_pressure_drop_unit("invalid"))
        
        # Check temperature units
        self.assertTrue(self.converter.is_valid_temperature_unit("K"))
        self.assertTrue(self.converter.is_valid_temperature_unit("C"))
        self.assertTrue(self.converter.is_valid_temperature_unit("F"))
        self.assertFalse(self.converter.is_valid_temperature_unit("invalid"))
        
        # Check mass units
        self.assertTrue(self.converter.is_valid_mass_unit("kg"))
        self.assertTrue(self.converter.is_valid_mass_unit("g"))
        self.assertTrue(self.converter.is_valid_mass_unit("t"))
        self.assertFalse(self.converter.is_valid_mass_unit("invalid"))
        
        # Check cost units
        self.assertTrue(self.converter.is_valid_cost_unit("USD"))
        self.assertTrue(self.converter.is_valid_cost_unit("EUR"))
        self.assertTrue(self.converter.is_valid_cost_unit("RUB"))
        self.assertFalse(self.converter.is_valid_cost_unit("invalid"))

if __name__ == '__main__':
    unittest.main() 