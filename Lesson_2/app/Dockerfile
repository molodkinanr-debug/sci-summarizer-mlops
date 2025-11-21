FROM python:3.12-slim
# Запускаем приложение
CMD ["python", "main.py"]

WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Копируем исходный код
COPY src/ .

# Открываем порт
EXPOSE 8080
