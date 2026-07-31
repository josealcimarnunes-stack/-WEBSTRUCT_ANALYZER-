# Usa a imagem oficial do Playwright com Python e Linux prontos
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia a lista de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do seu projeto para dentro do container
COPY . .

# Expõe a porta que a Render costuma usar
EXPOSE 10000

# Inicializa a aplicação Flask com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]