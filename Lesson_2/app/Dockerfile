FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
