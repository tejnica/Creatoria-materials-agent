import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from scholarly import scholarly
import arxiv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class WebSearchResult:
    title: str
    description: str
    url: str
    source: str
    properties: Dict[str, str]
    confidence: float

class WebMaterialSearcher:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setup_selenium()
        
    def setup_selenium(self):
        """Настройка Selenium для динамического контента"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_material(self, query: str, category: Optional[str] = None) -> List[WebSearchResult]:
        """Поиск материалов в различных источниках"""
        results = []
        
        # Поиск в Google Scholar
        scholar_results = await self._search_scholar(query)
        results.extend(scholar_results)
        
        # Поиск в arXiv
        arxiv_results = await self._search_arxiv(query)
        results.extend(arxiv_results)
        
        # Поиск в научных базах данных
        database_results = await self._search_databases(query)
        results.extend(database_results)
        
        # Поиск в общем интернете
        web_results = await self._search_web(query)
        results.extend(web_results)
        
        return results
    
    async def _search_scholar(self, query: str) -> List[WebSearchResult]:
        """Поиск в Google Scholar"""
        results = []
        try:
            search_query = scholarly.search_pubs(query)
            for i in range(5):  # Получаем первые 5 результатов
                try:
                    pub = next(search_query)
                    result = WebSearchResult(
                        title=pub.bib.get('title', ''),
                        description=pub.bib.get('abstract', ''),
                        url=pub.bib.get('url', ''),
                        source='Google Scholar',
                        properties=self._extract_properties(pub.bib.get('abstract', '')),
                        confidence=0.8
                    )
                    results.append(result)
                except StopIteration:
                    break
        except Exception as e:
            self.logger.error(f"Ошибка при поиске в Google Scholar: {str(e)}")
        return results
    
    async def _search_arxiv(self, query: str) -> List[WebSearchResult]:
        """Поиск в arXiv"""
        results = []
        try:
            search = arxiv.Search(
                query=query,
                max_results=5,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for result in search.results():
                result = WebSearchResult(
                    title=result.title,
                    description=result.summary,
                    url=result.entry_id,
                    source='arXiv',
                    properties=self._extract_properties(result.summary),
                    confidence=0.85
                )
                results.append(result)
        except Exception as e:
            self.logger.error(f"Ошибка при поиске в arXiv: {str(e)}")
        return results
    
    async def _search_databases(self, query: str) -> List[WebSearchResult]:
        """Поиск в научных базах данных"""
        results = []
        databases = [
            "https://www.sciencedirect.com",
            "https://www.nature.com",
            "https://www.springer.com"
        ]
        
        for db in databases:
            try:
                # Здесь должна быть реализация поиска для каждой базы данных
                # Это требует индивидуальной настройки для каждого источника
                pass
            except Exception as e:
                self.logger.error(f"Ошибка при поиске в {db}: {str(e)}")
        
        return results
    
    async def _search_web(self, query: str) -> List[WebSearchResult]:
        """Поиск в общем интернете"""
        results = []
        try:
            search_results = search(query, num_results=5)
            for url in search_results:
                try:
                    content = self._fetch_webpage(url)
                    if content:
                        result = WebSearchResult(
                            title=content.get('title', ''),
                            description=content.get('description', ''),
                            url=url,
                            source='Web',
                            properties=self._extract_properties(content.get('text', '')),
                            confidence=0.6
                        )
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке {url}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Ошибка при веб-поиске: {str(e)}")
        return results
    
    def _fetch_webpage(self, url: str) -> Optional[Dict]:
        """Получение содержимого веб-страницы"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Удаление ненужных элементов
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            return {
                'title': soup.title.string if soup.title else '',
                'description': self._get_meta_description(soup),
                'text': soup.get_text(separator=' ', strip=True)
            }
        except Exception as e:
            self.logger.error(f"Ошибка при получении страницы {url}: {str(e)}")
            return None
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Получение мета-описания страницы"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ''
    
    def _extract_properties(self, text: str) -> Dict[str, str]:
        """Извлечение свойств материала из текста"""
        properties = {}
        # Здесь должна быть реализация извлечения свойств
        # Например, поиск числовых значений с единицами измерения
        return properties
    
    def __del__(self):
        """Закрытие драйвера Selenium при уничтожении объекта"""
        try:
            self.driver.quit()
        except:
            pass 