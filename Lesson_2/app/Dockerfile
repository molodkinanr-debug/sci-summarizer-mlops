<<<<<<< HEAD
FROM python:3.9-slim
=======
FROM python:3.12-slim
# Запускаем приложение
CMD ["python", "main.py"]
>>>>>>> fa2889005cfcbe8d3705baf6ce79888b9fa07fa3

WORKDIR /app

# Копируем зависимости
<<<<<<< HEAD
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
=======
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
>>>>>>> fa2889005cfcbe8d3705baf6ce79888b9fa07fa3

# Копируем исходный код
COPY src/ .

# Открываем порт
<<<<<<< HEAD
EXPOSE 8000

# Запускаем приложение
CMD ["python", "main.py"]
=======
EXPOSE 8080
>>>>>>> fa2889005cfcbe8d3705baf6ce79888b9fa07fa3
