import yaml
import json
import requests
from typing import Dict, List, Optional, Set
import re
from dataclasses import dataclass
from pathlib import Path
import logging
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor
import spacy
from tenacity import retry, stop_after_attempt, wait_exponential
#from aci import ACI
from web_search import WebMaterialSearcher, WebSearchResult
from parameter_parser import ParameterParser, ParameterConstraint

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MaterialCategory(Enum):
    COMPOSITES = "composites"
    CERAMICS = "ceramics"
    METALS = "metals"
    POLYMERS = "polymers"
    NANOMATERIALS = "nanomaterials"

class ToxicityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Material:
    label: str
    formula: str
    thermal_conductivity: float  # λ
    density: float  # ρ
    max_temp: float  # temp_max
    young_modulus: float  # E
    yield_strength: float
    hardness: float
    cost: float
    toxicity: ToxicityLevel
    tags: List[str]

    def validate(self) -> List[str]:
        """Валидация данных материала"""
        errors = []
        
        if not self.label or len(self.label) < 2:
            errors.append("Название материала должно содержать минимум 2 символа")
        
        if not self.formula:
            errors.append("Химическая формула обязательна")
            
        if self.thermal_conductivity <= 0:
            errors.append("Теплопроводность должна быть положительной")
            
        if self.density <= 0:
            errors.append("Плотность должна быть положительной")
            
        if self.max_temp <= 0:
            errors.append("Максимальная температура должна быть положительной")
            
        if self.young_modulus <= 0:
            errors.append("Модуль Юнга должен быть положительным")
            
        if self.yield_strength <= 0:
            errors.append("Предел текучести должен быть положительным")
            
        if self.hardness <= 0:
            errors.append("Твердость должна быть положительной")
            
        if self.cost < 0:
            errors.append("Стоимость не может быть отрицательной")
            
        if not isinstance(self.toxicity, ToxicityLevel):
            errors.append("Уровень токсичности должен быть одним из: low, medium, high")
            
        if not self.tags:
            errors.append("Должен быть указан хотя бы один тег")
            
        return errors

class MaterialsAgent:
    def __init__(self, config_path: str = "config.json"):
        self.materials_file = Path("materials.yaml")
        self.existing_materials = self._load_existing_materials()
        self.nlp = spacy.load("en_core_web_sm")
        self.config = self._load_config()
        #self.aci = self._init_aci()
        self.web_searcher = WebMaterialSearcher(self.config) if self.config.get("web_search", {}).get("enabled", False) else None
        self.parameter_parser = ParameterParser()
        
    def _load_config(self) -> Dict:
        """Загрузка конфигурации"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Файл config.json не найден")
            raise
        
         
    def _load_existing_materials(self) -> Dict:
        try:
            if not self.materials_file.exists():
                return {category.value: [] for category in MaterialCategory}
            
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке материалов: {e}")
            return {category.value: [] for category in MaterialCategory}
    
    def _normalize_string(self, s: str) -> str:
        """Нормализация строки для сравнения"""
        return re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    
    def is_duplicate(self, material: Material) -> bool:
        """Проверка на дубликаты"""
        try:
            for category in self.existing_materials.values():
                for existing in category:
                    if (self._normalize_string(existing['label']) == self._normalize_string(material.label) or
                        self._normalize_string(existing['formula']) == self._normalize_string(material.formula)):
                        return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке дубликатов: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _search_materials_project(self, query: str) -> Optional[Dict]:
        """Поиск в Materials Project API"""
        if not self.config.get("materials_project"):
            logger.warning("API ключ Materials Project не найден")
            return None
            
        try:
            response = requests.get(
                f"https://api.materialsproject.org/materials/{query}",
                headers={"X-API-KEY": self.config["materials_project"]}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при поиске в Materials Project: {e}")
            return None

    async def _search_pubchem(self, query: str) -> Optional[Dict]:
    
    def _extract_tags(self, description: str) -> Set[str]:
            doc = self.nlp(description.lower())
            return {token.text for token in doc if token.is_alpha and not token.is_stop}

        """Извлечение тегов из описания материала"""
        doc = self.nlp(description.lower())
        
        # Базовые теги на основе ключевых слов
        tag_keywords = {
            "lightweight": ["light", "low density", "lightweight"],
            "conductive": ["conductive", "conductivity", "electrical"],
            "thermal": ["thermal", "heat", "temperature"],
            "structural": ["structural", "strength", "mechanical"],
            "aerospace": ["aerospace", "aircraft", "space"],
            "biocompatible": ["biocompatible", "bio", "medical"],
            "corrosion": ["corrosion", "rust", "resistant"],
            "magnetic": ["magnetic", "magnet", "ferromagnetic"],
            "optical": ["optical", "light", "transparent"],
            "ceramic": ["ceramic", "ceramics"],
            "metal": ["metal", "metallic"],
            "polymer": ["polymer", "plastic"],
            "composite": ["composite", "composites"],
            "nanomaterial": ["nano", "nanomaterial", "nanoparticle"]
        }
        
        tags = set()
        text = description.lower()
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.add(tag)
                
        return tags

    async def search_material(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Поиск материалов в различных источниках"""
        results = []
        
           
        # Поиск в интернете
        if self.web_searcher:
            try:
                web_results = await self.web_searcher.search_material(query, category)
                for result in web_results:
                    material = {
                        "name": result.title,
                        "description": result.description,
                        "category": category or self._determine_category(result.title, result.description),
                        "properties": result.properties,
                        "source": result.source,
                        "confidence": result.confidence,
                        "url": result.url
                    }
                    results.append(material)
            except Exception as e:
                logger.error(f"Ошибка при веб-поиске: {str(e)}")
        
        # Сортировка результатов по уверенности
        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return results

    def _determine_category(self, title: str, description: str) -> str:
        """Определение категории материала на основе текста"""
        text = f"{title} {description}".lower()
        max_matches = 0
        best_category = "other"
        
        for category, info in self.config["categories"].items():
            matches = sum(1 for keyword in info["keywords"] if keyword.lower() in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category

    def add_material(self, material: Material, category: str = "composites"):
        """Добавление материала в YAML"""
        try:
            # Валидация данных
            errors = material.validate()
            if errors:
                logger.error(f"Ошибки валидации материала {material.label}:")
                for error in errors:
                    logger.error(f"- {error}")
                return
            
            if self.is_duplicate(material):
                logger.warning(f"Материал {material.label} уже существует")
                return
            
            material_dict = {
                "label": material.label,
                "formula": material.formula,
                "λ": material.thermal_conductivity,
                "ρ": material.density,
                "temp_max": material.max_temp,
                "E": material.young_modulus,
                "yield_strength": material.yield_strength,
                "hardness": material.hardness,
                "cost": material.cost,
                "toxicity": material.toxicity.value,
                "tags": material.tags
            }
            
            if category not in self.existing_materials:
                self.existing_materials[category] = []
            
            self.existing_materials[category].append(material_dict)
            
            with open(self.materials_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.existing_materials, f, allow_unicode=True)
                
            logger.info(f"Материал {material.label} успешно добавлен в категорию {category}")
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении материала: {e}")
    
    def generate_n8n_json(self, category: str) -> Dict:
        """Генерация JSON для n8n"""
        try:
            return {
                "name": "AI Materials Importer",
                "nodes": [
                    {
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "materials-webhook",
                            "responseMode": "onReceived"
                        },
                        "id": "Webhook Trigger",
                        "name": "Webhook",
                        "type": "n8n-nodes-base.webhook"
                    },
                    {
                        "parameters": {
                            "functionCode": f"// Преобразование JSON в YAML\nconst yaml = require('js-yaml');\nconst input = items[0].json;\n\nconst grouped = {{ {category}: input.{category} }};\nreturn [{{ json: {{ yaml: yaml.dump(grouped) }} }}];"
                        },
                        "id": "YAML Generator",
                        "name": "Convert to YAML",
                        "type": "n8n-nodes-base.function"
                    },
                    {
                        "parameters": {
                            "owner": "creatoria-labs",
                            "repository": "materials-database",
                            "filePath": f"data/materials-{category}.yaml",
                            "content": "={{$json[\"yaml\"]}}",
                            "branch": "main",
                            "commitMessage": f"Auto-upload: new {category} material"
                        },
                        "id": "GitHub Push",
                        "name": "Upload to GitHub",
                        "type": "n8n-nodes-base.github"
                    }
                ],
                "connections": {
                    "Webhook": {
                        "main": [["Convert to YAML"]]
                    },
                    "Convert to YAML": {
                        "main": [["Upload to GitHub"]]
                    }
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при генерации JSON для n8n: {e}")
            return {}

    async def search_by_parameters(self, query: str) -> List[Dict]:
        """Поиск материалов по параметрам"""
        try:
            # Парсим параметры из запроса
            constraints = self.parameter_parser.parse_query(query)
            if not constraints:
                logger.warning("Не удалось распознать параметры в запросе")
                return []

            # Поиск материалов в различных источниках
            results = []
            
            # Поиск в существующих материалах
            for category, materials in self.existing_materials.items():
                for material in materials:
                    if self._check_material_constraints(material, constraints):
                        results.append({
                            "name": material["label"],
                            "description": f"Найден в категории {category}",
                            "category": category,
                            "properties": self._extract_material_properties(material),
                            "source": "local_database",
                            "confidence": 1.0
                        })

            # Поиск в интернете
            if self.web_searcher:
                web_results = await self.web_searcher.search_material(
                    self._generate_search_query(constraints)
                )
                for result in web_results:
                    if self._check_web_result_constraints(result, constraints):
                        results.append(result)

            # Сортировка результатов по количеству удовлетворенных ограничений
            results.sort(key=lambda x: self._count_satisfied_constraints(x, constraints), reverse=True)
            
            return results

        except Exception as e:
            logger.error(f"Ошибка при поиске по параметрам: {str(e)}")
            return []

    def _check_material_constraints(self, material: Dict, constraints: List[ParameterConstraint]) -> bool:
        """Проверка соответствия материала ограничениям"""
        for constraint in constraints:
            if not self._check_constraint(material, constraint):
                return False
        return True

    def _check_web_result_constraints(self, result: WebSearchResult, constraints: List[ParameterConstraint]) -> bool:
        """Проверка соответствия веб-результата ограничениям"""
        properties = result.properties
        for constraint in constraints:
            if not self._check_constraint(properties, constraint):
                return False
        return True

    def _check_constraint(self, data: Dict, constraint: ParameterConstraint) -> bool:
        """Проверка одного ограничения"""
        value = data.get(constraint.name)
        if value is None:
            return False

        # Конвертируем единицы измерения если необходимо
        if constraint.unit and isinstance(value, (int, float)):
            value = self.parameter_parser.convert_unit(value, data.get(f"{constraint.name}_unit", ""), constraint.unit)

        if constraint.operator == "less_equal":
            return value <= constraint.value
        elif constraint.operator == "greater_equal":
            return value >= constraint.value
        elif constraint.operator == "less":
            return value < constraint.value
        elif constraint.operator == "greater":
            return value > constraint.value
        elif constraint.operator == "equal":
            return value == constraint.value
        elif constraint.operator == "range":
            return constraint.range_min <= value <= constraint.range_max

        return False

    def _count_satisfied_constraints(self, result: Dict, constraints: List[ParameterConstraint]) -> int:
        """Подсчет количества удовлетворенных ограничений"""
        count = 0
        for constraint in constraints:
            if self._check_constraint(result.get("properties", {}), constraint):
                count += 1
        return count

    def _generate_search_query(self, constraints: List[ParameterConstraint]) -> str:
        """Генерация поискового запроса на основе ограничений"""
        query_parts = []
        for constraint in constraints:
            query_parts.append(f"{constraint.name} {constraint.value} {constraint.unit}")
        return " ".join(query_parts)

    def _extract_material_properties(self, material: Dict) -> Dict:
        """Извлечение свойств материала в стандартный формат"""
        return {
            "pressure": material.get("pressure", 0),
            "temperature": material.get("temperature", 0),
            "mass": material.get("mass", 0),
            "cost": material.get("cost", 0),
            "density": material.get("density", 0),
            "thermal_conductivity": material.get("thermal_conductivity", 0),
            "electrical_conductivity": material.get("electrical_conductivity", 0),
            "strength": material.get("strength", 0),
            "hardness": material.get("hardness", 0)
        }

async def main():
    try:
        agent = MaterialsAgent()
        
        # Пример использования
        material = await agent.search_material("graphene")
        if material:
            agent.add_material(material, MaterialCategory.NANOMATERIALS.value)
            
            # Генерация JSON для n8n
            n8n_json = agent.generate_n8n_json(MaterialCategory.NANOMATERIALS.value)
            with open("materials-upload.json", "w") as f:
                json.dump(n8n_json, f, indent=2)
                
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
