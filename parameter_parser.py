import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParameterConstraint:
    name: str
    operator: str
    value: float
    unit: str
    range_min: Optional[float] = None
    range_max: Optional[float] = None

class ParameterParser:
    def __init__(self):
        self.unit_patterns = {
            'pressure': r'(kPa|MPa|Pa|bar|psi)',
            'temperature': r'(°C|K|°F)',
            'mass': r'(kg|g|mg)',
            'cost': r'(\$|€|£|USD|EUR|GBP)',
            'length': r'(m|cm|mm|in|ft)',
            'time': r'(s|min|h|hr)',
            'volume': r'(L|ml|m³|cm³)',
            'density': r'(kg/m³|g/cm³)',
            'thermal_conductivity': r'(W/m·K|W/mK)',
            'electrical_conductivity': r'(S/m|Ω·m)',
            'strength': r'(MPa|GPa|N/m²)',
            'hardness': r'(HV|HRC|HB)'
        }
        
        self.operator_patterns = {
            '≤': 'less_equal',
            '≥': 'greater_equal',
            '<': 'less',
            '>': 'greater',
            '=': 'equal',
            '==': 'equal',
            '–': 'range',  # en dash
            '-': 'range'   # hyphen
        }
        
        self.parameter_mapping = {
            'pressure drop': 'pressure',
            'inlet temperature': 'temperature',
            'mass': 'mass',
            'cost': 'cost',
            'length': 'length',
            'density': 'density',
            'thermal conductivity': 'thermal_conductivity',
            'electrical conductivity': 'electrical_conductivity',
            'strength': 'strength',
            'hardness': 'hardness'
        }

    def parse_query(self, query: str) -> List[ParameterConstraint]:
        """Парсинг параметрического запроса"""
        constraints = []
        
        # Разбиваем запрос на строки
        lines = [line.strip() for line in query.split('\n') if line.strip()]
        
        for line in lines:
            try:
                # Удаляем маркеры списка и лишние пробелы
                line = re.sub(r'^[-•*]\s*', '', line)
                
                # Парсим параметр
                constraint = self._parse_line(line)
                if constraint:
                    constraints.append(constraint)
            except Exception as e:
                logger.error(f"Ошибка при парсинге строки '{line}': {str(e)}")
                continue
        
        return constraints

    def _parse_line(self, line: str) -> Optional[ParameterConstraint]:
        """Парсинг одной строки с параметром"""
        # Ищем оператор
        operator = None
        operator_pos = -1
        for op in self.operator_patterns.keys():
            pos = line.find(op)
            if pos != -1 and (operator_pos == -1 or pos < operator_pos):
                operator = op
                operator_pos = pos
        
        if not operator:
            return None
            
        # Разделяем на имя параметра и значение
        parts = line.split(operator)
        if len(parts) != 2:
            return None
            
        param_name = parts[0].strip().lower()
        value_part = parts[1].strip()
        
        # Нормализуем имя параметра
        normalized_name = self._normalize_parameter_name(param_name)
        if not normalized_name:
            return None
            
        # Парсим значение и единицу измерения
        value, unit = self._parse_value_and_unit(value_part)
        if value is None:
            return None
            
        # Обработка диапазона значений
        range_min = None
        range_max = None
        if self.operator_patterns[operator] == 'range':
            range_min, range_max = value
        
        return ParameterConstraint(
            name=normalized_name,
            operator=self.operator_patterns[operator],
            value=value if not isinstance(value, tuple) else value[1],
            unit=unit,
            range_min=range_min,
            range_max=range_max
        )

    def _normalize_parameter_name(self, name: str) -> Optional[str]:
        """Нормализация имени параметра"""
        name = name.lower().strip()
        return self.parameter_mapping.get(name)

    def _parse_value_and_unit(self, text: str) -> Tuple[Optional[float], str]:
        """Парсинг значения и единицы измерения"""
        # Удаляем все пробелы
        text = text.replace(' ', '')
        
        # Ищем число
        number_match = re.search(r'[-+]?\d*\.?\d+', text)
        if not number_match:
            return None, ''
            
        value = float(number_match.group())
        
        # Ищем единицу измерения
        unit = ''
        for param_type, pattern in self.unit_patterns.items():
            unit_match = re.search(pattern, text)
            if unit_match:
                unit = unit_match.group()
                break
                
        return value, unit

    def convert_unit(self, value: float, from_unit: str, to_unit: str) -> float:
        """Конвертация единиц измерения"""
        # Таблица конвертации для основных единиц
        conversion_table = {
            'pressure': {
                'kPa': {'Pa': 1000, 'MPa': 0.001, 'bar': 0.01, 'psi': 0.145038},
                'MPa': {'kPa': 1000, 'Pa': 1000000, 'bar': 10, 'psi': 145.038},
                'Pa': {'kPa': 0.001, 'MPa': 0.000001, 'bar': 0.00001, 'psi': 0.000145038},
                'bar': {'kPa': 100, 'MPa': 0.1, 'Pa': 100000, 'psi': 14.5038},
                'psi': {'kPa': 6.89476, 'MPa': 0.00689476, 'Pa': 6894.76, 'bar': 0.0689476}
            },
            'temperature': {
                '°C': {'K': lambda x: x + 273.15, '°F': lambda x: x * 9/5 + 32},
                'K': {'°C': lambda x: x - 273.15, '°F': lambda x: (x - 273.15) * 9/5 + 32},
                '°F': {'°C': lambda x: (x - 32) * 5/9, 'K': lambda x: (x - 32) * 5/9 + 273.15}
            },
            'mass': {
                'kg': {'g': 1000, 'mg': 1000000},
                'g': {'kg': 0.001, 'mg': 1000},
                'mg': {'kg': 0.000001, 'g': 0.001}
            }
        }
        
        # Определяем тип параметра
        param_type = None
        for type_name, units in conversion_table.items():
            if from_unit in units and to_unit in units[from_unit]:
                param_type = type_name
                break
                
        if not param_type:
            return value
            
        # Выполняем конвертацию
        if param_type == 'temperature':
            return conversion_table[param_type][from_unit][to_unit](value)
        else:
            return value * conversion_table[param_type][from_unit][to_unit] 