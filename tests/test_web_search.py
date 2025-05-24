import unittest
from unittest.mock import Mock, patch
from web_search import WebSearcher

class TestWebSearcher(unittest.TestCase):
    def setUp(self):
        self.searcher = WebSearcher()

    @patch('web_search.WebSearcher._search_google_scholar')
    def test_search_google_scholar(self, mock_search):
        # Настраиваем мок
        mock_search.return_value = [
            {
                "title": "Test Paper 1",
                "abstract": "This is a test paper about materials",
                "url": "http://example.com/paper1",
                "source": "google_scholar"
            }
        ]

        # Тестируем поиск
        results = self.searcher.search_google_scholar("test materials")
        
        # Проверяем результаты
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Paper 1")
        self.assertEqual(results[0]["source"], "google_scholar")

    @patch('web_search.WebSearcher._search_arxiv')
    def test_search_arxiv(self, mock_search):
        # Настраиваем мок
        mock_search.return_value = [
            {
                "title": "Test Paper 2",
                "abstract": "This is another test paper",
                "url": "http://arxiv.org/paper2",
                "source": "arxiv"
            }
        ]

        # Тестируем поиск
        results = self.searcher.search_arxiv("test materials")
        
        # Проверяем результаты
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Paper 2")
        self.assertEqual(results[0]["source"], "arxiv")

    @patch('web_search.WebSearcher._search_sciencedirect')
    def test_search_sciencedirect(self, mock_search):
        # Настраиваем мок
        mock_search.return_value = [
            {
                "title": "Test Paper 3",
                "abstract": "This is a ScienceDirect paper",
                "url": "http://sciencedirect.com/paper3",
                "source": "sciencedirect"
            }
        ]

        # Тестируем поиск
        results = self.searcher.search_sciencedirect("test materials")
        
        # Проверяем результаты
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Paper 3")
        self.assertEqual(results[0]["source"], "sciencedirect")

    def test_extract_material_properties(self):
        text = """
        The material has a pressure drop of 50 Pa/m and can operate at temperatures up to 350 K.
        Its mass is 500 kg and costs 2500 USD.
        """
        
        properties = self.searcher.extract_material_properties(text)
        
        self.assertEqual(properties["pressure_drop"], 50)
        self.assertEqual(properties["inlet_temperature"], 350)
        self.assertEqual(properties["mass"], 500)
        self.assertEqual(properties["cost"], 2500)

    def test_extract_material_properties_no_match(self):
        text = "This text doesn't contain any material properties."
        
        properties = self.searcher.extract_material_properties(text)
        
        self.assertEqual(properties, {})

    @patch('web_search.WebSearcher.search_google_scholar')
    @patch('web_search.WebSearcher.search_arxiv')
    @patch('web_search.WebSearcher.search_sciencedirect')
    def test_search_all_sources(self, mock_sciencedirect, mock_arxiv, mock_scholar):
        # Настраиваем моки
        mock_scholar.return_value = [
            {
                "title": "Test Paper 1",
                "abstract": "This is a test paper",
                "url": "http://example.com/paper1",
                "source": "google_scholar"
            }
        ]
        
        mock_arxiv.return_value = [
            {
                "title": "Test Paper 2",
                "abstract": "This is another test paper",
                "url": "http://arxiv.org/paper2",
                "source": "arxiv"
            }
        ]
        
        mock_sciencedirect.return_value = [
            {
                "title": "Test Paper 3",
                "abstract": "This is a third test paper",
                "url": "http://sciencedirect.com/paper3",
                "source": "sciencedirect"
            }
        ]

        # Тестируем поиск по всем источникам
        results = self.searcher.search_all_sources("test materials")
        
        # Проверяем результаты
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["source"], "google_scholar")
        self.assertEqual(results[1]["source"], "arxiv")
        self.assertEqual(results[2]["source"], "sciencedirect")

if __name__ == '__main__':
    unittest.main() 