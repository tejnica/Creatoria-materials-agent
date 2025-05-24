FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY . .

# Запуск приложения
CMD ["uvicorn", "run_agent:app", "--host", "0.0.0.0", "--port", "8000"] 