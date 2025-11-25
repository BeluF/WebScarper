FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Playwright
# Usamos los nombres de paquetes actualizados para Debian Bookworm
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Dependencias de Chromium
    libnss3 \
    libnspr4 \
    libatk1. 0-0 \
    libatk-bridge2. 0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Fuentes (nombres actualizados)
    fonts-unifont \
    fonts-ubuntu \
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements. txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y el navegador Chromium
RUN playwright install chromium
# Ya no necesitamos 'playwright install-deps' porque instalamos las dependencias arriba

# Copiar código de la aplicación
COPY .  .

# Exponer puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0. 0", "--port", "8000", "--reload"]
