import unittest
from parameter_parser import ParameterParser

class TestParameterParser(unittest.TestCase):
    def setUp(self):
        self.parser = ParameterParser()

    def test_parse_simple_query(self):
        query = "pressure_drop < 100 Pa/m"
        result = self.parser.parse(query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parameter"], "pressure_drop")
        self.assertEqual(result[0]["operator"], "<")
        self.assertEqual(result[0]["value"], 100)
        self.assertEqual(result[0]["unit"], "Pa/m")

    def test_parse_complex_query(self):
        query = "pressure_drop < 100 Pa/m AND inlet_temperature > 300 K AND mass < 1000 kg"
        result = self.parser.parse(query)
        self.assertEqual(len(result), 3)
        
        # Проверяем первый параметр
        self.assertEqual(result[0]["parameter"], "pressure_drop")
        self.assertEqual(result[0]["operator"], "<")
        self.assertEqual(result[0]["value"], 100)
        self.assertEqual(result[0]["unit"], "Pa/m")
        
        # Проверяем второй параметр
        self.assertEqual(result[1]["parameter"], "inlet_temperature")
        self.assertEqual(result[1]["operator"], ">")
        self.assertEqual(result[1]["value"], 300)
        self.assertEqual(result[1]["unit"], "K")
        
        # Проверяем третий параметр
        self.assertEqual(result[2]["parameter"], "mass")
        self.assertEqual(result[2]["operator"], "<")
        self.assertEqual(result[2]["value"], 1000)
        self.assertEqual(result[2]["unit"], "kg")

    def test_parse_with_cost(self):
        query = "cost < 5000 USD"
        result = self.parser.parse(query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parameter"], "cost")
        self.assertEqual(result[0]["operator"], "<")
        self.assertEqual(result[0]["value"], 5000)
        self.assertEqual(result[0]["unit"], "USD")

    def test_parse_invalid_query(self):
        with self.assertRaises(ValueError):
            self.parser.parse("invalid query")

    def test_parse_empty_query(self):
        with self.assertRaises(ValueError):
            self.parser.parse("")

    def test_parse_without_unit(self):
        query = "pressure_drop < 100"
        with self.assertRaises(ValueError):
            self.parser.parse(query)

if __name__ == '__main__':
    unittest.main() 