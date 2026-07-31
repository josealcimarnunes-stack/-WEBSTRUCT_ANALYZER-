FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Cria pasta de dados do banco se não existir
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]