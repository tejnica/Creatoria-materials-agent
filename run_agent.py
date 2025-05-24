import asyncio
import json
import logging
from pathlib import Path
from creatoria_agent import MaterialsAgent, MaterialCategory
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Optional, List, Dict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='agent.log'
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(title="Creatoria Materials Agent")

# Модель для входящих данных
class MaterialRequest(BaseModel):
    query: str
    category: Optional[str] = None
    parameters: Optional[str] = None

# Глобальный экземпляр агента
agent = None

@app.on_event("startup")
async def startup_event():
    """Инициализация агента при запуске сервера"""
    global agent
    try:
        agent = MaterialsAgent()
        logger.info("Агент успешно инициализирован")
    except Exception as e:
        logger.error(f"Ошибка при инициализации агента: {e}")
        raise

@app.post("/materials-webhook")
async def materials_webhook(request: MaterialRequest):
    """Webhook для получения запросов от n8n"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Агент не инициализирован")

        # Если есть параметрический запрос, используем его
        if request.parameters:
            results = await agent.search_by_parameters(request.parameters)
        else:
            # Обычный поиск по ключевым словам
            results = await agent.search_material(request.query, request.category)

        # Генерация JSON для n8n
        n8n_json = agent.generate_n8n_json(request.category or "other")
        
        # Сохранение результатов
        with open("materials-upload.json", "w") as f:
            json.dump(n8n_json, f, indent=2)
        
        return {
            "status": "success",
            "results": results,
            "n8n_json": n8n_json
        }
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/health")
async def health_check():
    """Проверка работоспособности сервера"""
    return {"status": "healthy"}

async def run_agent_once():
    """Запуск агента для однократного поиска"""
    try:
        material = await agent.search_material("graphene")
        if material:
            agent.add_material(material, MaterialCategory.NANOMATERIALS.value)
            n8n_json = agent.generate_n8n_json(MaterialCategory.NANOMATERIALS.value)
            with open("materials-upload.json", "w") as f:
                json.dump(n8n_json, f, indent=2)
            logger.info(f"Материал {material.label} успешно обработан")
    except Exception as e:
        logger.error(f"Ошибка при запуске агента: {e}")

def main():
    """Основная функция запуска"""
    # Запуск FastAPI сервера
    uvicorn.run(
        "run_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main() 