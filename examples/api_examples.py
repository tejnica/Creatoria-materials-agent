import requests
import json

# Базовый URL API
BASE_URL = "http://localhost:8000"

def search_by_parameters():
    """Пример поиска материалов по параметрам"""
    url = f"{BASE_URL}/materials-webhook"
    
    # Пример запроса с параметрами
    data = {
        "query": "pressure_drop < 100 Pa/m AND inlet_temperature > 300 K AND mass < 1000 kg AND cost < 5000 USD",
        "category": "metals"
    }
    
    response = requests.post(url, json=data)
    print("Поиск по параметрам:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def search_by_keywords():
    """Пример поиска материалов по ключевым словам"""
    url = f"{BASE_URL}/materials-webhook"
    
    # Пример запроса с ключевыми словами
    data = {
        "query": "high temperature steel alloy",
        "category": "metals"
    }
    
    response = requests.post(url, json=data)
    print("\nПоиск по ключевым словам:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def check_health():
    """Проверка работоспособности сервера"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print("\nПроверка работоспособности:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Проверяем работоспособность сервера
    check_health()
    
    # Выполняем поиск по параметрам
    search_by_parameters()
    
    # Выполняем поиск по ключевым словам
    search_by_keywords() 