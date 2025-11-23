FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Открываем порт
EXPOSE 8080

# Копируем исходный код
COPY ./ /app

# Запускаем приложение
CMD ["python", "main.py"]
