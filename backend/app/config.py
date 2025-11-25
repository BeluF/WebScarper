"""
Configuración del proyecto WebScarper.

Este módulo centraliza todas las configuraciones del sistema,
incluyendo base de datos, rutas de archivos y opciones del scraper.
"""

import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de base de datos SQLite
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/recetario.db")

# Configuración del scraper
SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "30000"))  # milisegundos
SCRAPER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"

# Rate limiting - tiempo de espera entre peticiones (segundos)
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "2.0"))

# Configuración de proxies (opcional)
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "false").lower() == "true"
PROXY_LIST_FILE = os.getenv("PROXY_LIST_FILE", str(BASE_DIR / "proxies.txt"))

# Configuración de la API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# Configuración de CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Configuración de PDF
PDF_TEMP_DIR = os.getenv("PDF_TEMP_DIR", "/tmp/recetario_pdfs")
