import unittest
from parameter_parser import ErrorHandler
from creatoria_agent import MaterialsAgent
from web_search import WebSearcher

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler()
        self.agent = MaterialsAgent()
        self.searcher = WebSearcher()

    def test_validation_error(self):
        """Test validation error handling"""
        # Invalid category
        with self.assertRaises(ValueError) as context:
            self.agent.search_by_parameters("pressure_drop < 100 Pa/m", "invalid_category")
        self.assertIn("Invalid category", str(context.exception))

        # Invalid query
        with self.assertRaises(ValueError) as context:
            self.agent.search_by_parameters("invalid query", "metals")
        self.assertIn("Invalid query", str(context.exception))

        # Missing unit
        with self.assertRaises(ValueError) as context:
            self.agent.search_by_parameters("pressure_drop < 100", "metals")
        self.assertIn("Missing unit", str(context.exception))

    def test_network_error(self):
        """Test network error handling"""
        # API connection error
        with self.assertRaises(ConnectionError) as context:
            self.searcher.search_google_scholar("test")
        self.assertIn("Failed to connect", str(context.exception))

        # Request timeout
        with self.assertRaises(TimeoutError) as context:
            self.searcher.search_arxiv("test")
        self.assertIn("Request timed out", str(context.exception))

        # HTTP error
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.searcher.search_sciencedirect("test")
        self.assertIn("HTTP error", str(context.exception))

    def test_parsing_error(self):
        """Test parsing error handling"""
        # Invalid data format
        with self.assertRaises(ValueError) as context:
            self.agent.parse_material_data("invalid data")
        self.assertIn("Invalid data format", str(context.exception))

        # Missing required fields
        with self.assertRaises(ValueError) as context:
            self.agent.parse_material_data({"name": "Test"})
        self.assertIn("Missing required fields", str(context.exception))

        # Invalid values
        with self.assertRaises(ValueError) as context:
            self.agent.parse_material_data({
                "name": "Test",
                "category": "metals",
                "properties": {
                    "pressure_drop": "invalid"
                }
            })
        self.assertIn("Invalid property value", str(context.exception))

    def test_conversion_error(self):
        """Test unit conversion error handling"""
        # Invalid unit
        with self.assertRaises(ValueError) as context:
            self.agent.convert_unit(100, "invalid", "Pa/m")
        self.assertIn("Invalid unit", str(context.exception))

        # Invalid value
        with self.assertRaises(ValueError) as context:
            self.agent.convert_unit("invalid", "Pa/m", "kPa/m")
        self.assertIn("Invalid value", str(context.exception))

        # Invalid conversion
        with self.assertRaises(ValueError) as context:
            self.agent.convert_unit(100, "Pa/m", "K")
        self.assertIn("Incompatible units", str(context.exception))

    def test_storage_error(self):
        """Test storage error handling"""
        # File write error
        with self.assertRaises(IOError) as context:
            self.agent.save_materials("invalid/path/materials.yaml")
        self.assertIn("Failed to save", str(context.exception))

        # File read error
        with self.assertRaises(IOError) as context:
            self.agent.load_materials("invalid/path/materials.yaml")
        self.assertIn("Failed to load", str(context.exception))

        # File access error
        with self.assertRaises(PermissionError) as context:
            self.agent.save_materials("/root/materials.yaml")
        self.assertIn("Permission denied", str(context.exception))

    def test_retry_mechanism(self):
        """Test retry mechanism"""
        # Check retry count
        self.assertEqual(self.error_handler.get_retry_count(), 0)
        
        # Perform operation with error
        try:
            self.agent.search_by_parameters("pressure_drop < 100 Pa/m", "invalid_category")
        except ValueError:
            pass
        
        # Check that attempt was counted
        self.assertEqual(self.error_handler.get_retry_count(), 1)
        
        # Reset counter
        self.error_handler.reset_retry_count()
        self.assertEqual(self.error_handler.get_retry_count(), 0)

    def test_error_logging(self):
        """Test error logging"""
        # Check that error is logged
        try:
            self.agent.search_by_parameters("pressure_drop < 100 Pa/m", "invalid_category")
        except ValueError as e:
            self.error_handler.log_error(e)
        
        # Check log entry
        with open("materials_agent.log") as f:
            log_content = f.read()
        self.assertIn("ERROR", log_content)
        self.assertIn("Invalid category", log_content)

if __name__ == '__main__':
    unittest.main() 