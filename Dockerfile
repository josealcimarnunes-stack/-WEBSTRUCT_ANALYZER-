FROM python:3.10-slim

WORKDIR /app

# ⭐ INSTALA O CHROME ⭐
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ⭐ COPIA E INSTALA DEPENDÊNCIAS ⭐
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ⭐ COPIA O CÓDIGO ⭐
COPY . .

# ⭐ EXPÕE A PORTA ⭐
EXPOSE 5000

# ⭐ RODA O APP ⭐
CMD ["python", "main.py"]