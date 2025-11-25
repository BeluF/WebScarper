# 🍳 WebScarper - Recetario Personal con Web Scraping

Sistema web completo para crear un recetario personal privado mediante web scraping. Permite extraer recetas de múltiples sitios web, categorizarlas y exportarlas a PDF.

## ✨ Características

- **Scraping de Recetas**: Pega una URL y obtén automáticamente título, ingredientes, pasos, tiempos e imagen
- **10 Sitios Soportados**: Cookpad, AllRecipes, Tasty, Directo al Paladar, Paulina Cocina, HelloFresh, y más
- **Categorización**: Marca recetas como Sin TACC, Vegetariana o Vegana
- **Filtrado y Búsqueda**: Encuentra tus recetas fácilmente
- **Exportación PDF**: Descarga recetas individuales o múltiples en un elegante PDF
- **Notificaciones**: Feedback visual cuando el scraping termina
- **Preparado para Proxies**: Estructura lista para rotación de proxies

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.11+** con **FastAPI**
- **SQLite** como base de datos (ligera, un solo archivo)
- **Playwright** para scraping (soporta JavaScript)
- **SQLAlchemy** como ORM
- **ReportLab** para generación de PDF

### Frontend
- **React 18** con **TypeScript**
- **Vite** como bundler
- **Tailwind CSS** para estilos
- **React Hot Toast** para notificaciones
- **Axios** para llamadas API

### DevOps
- **Docker** y **docker-compose**

## 📋 Requisitos Previos

### Con Docker (Recomendado)
- Docker 20.10+
- Docker Compose 2.0+

### Sin Docker
- Python 3.11+
- Node.js 18+
- npm 9+

## 🚀 Instalación

### Opción 1: Con Docker (Recomendada)

1. **Clonar el repositorio**
```bash
git clone https://github.com/BeluF/WebScarper.git
cd WebScarper
```

2. **Copiar el archivo de configuración**
```bash
cp .env.example .env
```

3. **Construir e iniciar los contenedores**
```bash
docker-compose up --build
```

4. **Acceder a la aplicación**
- Frontend: http://localhost:80
- API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Opción 2: Sin Docker

#### Backend

1. **Crear y activar entorno virtual**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows: venv\Scripts\activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Instalar navegador de Playwright**
```bash
playwright install chromium
```

4. **Iniciar el servidor**
```bash
uvicorn app.main:app --reload --port 8000
```

#### Frontend

1. **Instalar dependencias**
```bash
cd frontend
npm install
```

2. **Iniciar el servidor de desarrollo**
```bash
npm run dev
```

3. **Acceder a la aplicación**
- Frontend: http://localhost:5173
- API: http://localhost:8000

## 📖 Cómo Usar

### Agregar una Receta

1. Copia la URL de una receta de cualquier sitio soportado
2. Pega la URL en el campo de texto de la página principal
3. Haz clic en "Scrapear"
4. ¡Listo! La receta se guardará automáticamente

### Categorizar Recetas

1. Abre una receta haciendo clic en "Ver receta"
2. Haz clic en "Editar"
3. Marca las categorías correspondientes (Sin TACC, Vegetariana, Vegana)
4. Guarda los cambios

### Exportar a PDF

**Receta individual:**
1. Abre la receta
2. Haz clic en "Descargar PDF"

**Múltiples recetas:**
1. En la página principal, selecciona las recetas con el checkbox
2. Haz clic en "Descargar PDF (N)"

## 🌐 Sitios Web Soportados

| Sitio | Dominio |
|-------|---------|
| Cookpad | cookpad.com |
| AllRecipes | allrecipes.com |
| Tasty | tasty.co |
| Directo al Paladar | directoalpaladar.com |
| Recetas de Rechupete | recetasderechupete.com |
| Paulina Cocina | paulinacocina.net |
| Soy Celíaco No Extraterrestre | soyceliaconoextraterrestre.com |
| HelloFresh | hellofresh.com |
| Cocineros Argentinos | cocinerosargentinos.com |
| Recetas Essen | recetasessen.com.ar |

## 🔧 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/recetas` | Listar recetas (con filtros) |
| GET | `/api/recetas/{id}` | Obtener receta por ID |
| POST | `/api/recetas/scrapear` | Scrapear nueva receta |
| PUT | `/api/recetas/{id}` | Actualizar receta |
| DELETE | `/api/recetas/{id}` | Eliminar receta |
| GET | `/api/recetas/{id}/pdf` | Descargar PDF individual |
| POST | `/api/recetas/pdf-multiple` | Descargar PDF múltiple |
| GET | `/api/health` | Health check |
| GET | `/api/sitios-soportados` | Lista de sitios soportados |

## 🧩 Agregar Nuevos Scrapers

Para agregar soporte para un nuevo sitio:

1. **Crear el scraper** en `backend/app/scraper/sites/nuevo_sitio.py`:

```python
from app.scraper.base_scraper import BaseScraper, RecetaScraped

class NuevoSitioScraper(BaseScraper):
    nombre_sitio = "Nuevo Sitio"
    dominios_soportados = ["nuevositio.com"]
    
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        # Extraer título
        titulo = await self._extraer_texto_seguro(page, 'h1.titulo')
        
        # Extraer ingredientes
        ingredientes = await self._extraer_lista_textos(page, '.ingredientes li')
        
        # Extraer pasos
        pasos = await self._extraer_lista_textos(page, '.pasos li')
        
        return RecetaScraped(
            titulo=titulo,
            url_origen=url,
            sitio_origen=self.nombre_sitio,
            ingredientes=ingredientes,
            pasos=pasos
        )
```

2. **Registrar el scraper** en `backend/app/scraper/sites/__init__.py`:

```python
from app.scraper.sites.nuevo_sitio import NuevoSitioScraper
```

3. **Agregar a la factory** en `backend/app/scraper/scraper_factory.py`:

```python
from app.scraper.sites import NuevoSitioScraper
# Agregar a la lista _scrapers
```

## 🔐 Configuración de Proxies (Opcional)

Para usar proxies y evitar bloqueos:

1. **Crear archivo de proxies** `proxies.txt`:
```
http://proxy1:8080
http://usuario:contraseña@proxy2:8080
socks5://proxy3:1080
```

2. **Activar en configuración** (`.env`):
```env
PROXY_ENABLED=true
PROXY_LIST_FILE=./proxies.txt
```

## 📁 Estructura del Proyecto

```
WebScarper/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── scraper/      # Lógica de scraping
│   │   │   └── sites/    # Scrapers por sitio
│   │   └── services/     # Servicios (PDF, recetas)
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── pages/        # Páginas
│   │   ├── services/     # Cliente API
│   │   └── types/        # Tipos TypeScript
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🧪 Ejecutar Tests

### Backend
```bash
cd backend
pytest tests/
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📧 Contacto

Si tienes preguntas o sugerencias, abre un issue en el repositorio.

---

Hecho con ❤️ para los amantes de la cocina
