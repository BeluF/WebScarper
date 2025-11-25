"""
Scraper para HelloFresh (hellofresh.es / hellofresh.com.ar).

Servicio de kits de comida con recetas detalladas.
Usa las versiones en español del sitio.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class HelloFreshScraper(BaseScraper):
    """
    Scraper especializado para HelloFresh.
    
    Extrae recetas del sitio hellofresh.es (versión en español).
    """
    
    nombre_sitio = "HelloFresh"
    # Priorizamos los dominios en español
    dominios_soportados = ["hellofresh.es", "hellofresh.com.ar", "hellofresh.com"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """
        Construye la URL de búsqueda para HelloFresh.
        
        Usa la versión española del sitio para obtener recetas en español.
        """
        # Usar la versión en español del sitio
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://www.hellofresh.es/recipes/search?q={query}"
        return "https://www.hellofresh.es/recipes"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """Extrae la lista de recetas de la página de búsqueda."""
        recetas = []
        selectores = ['a[href*="/recipes/"]', '[data-test-id*="recipe-card"] a']
        
        for selector in selectores:
            try:
                elementos = await page.query_selector_all(selector)
                for elemento in elementos[:limite]:
                    try:
                        href = await elemento.get_attribute("href")
                        if not href or "/recipes/" not in href:
                            continue
                        if href.startswith("/"):
                            href = f"https://www.hellofresh.com{href}"
                        titulo_elem = await elemento.query_selector('h3, .recipe-card-title')
                        titulo = ""
                        if titulo_elem:
                            titulo = (await titulo_elem.inner_text()).strip()
                        if href:
                            recetas.append({"url": href, "titulo": titulo, "imagen_preview": ""})
                        if len(recetas) >= limite:
                            break
                    except Exception:
                        continue
                if recetas:
                    break
            except Exception:
                continue
        return recetas[:limite]
    
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        """
        Extrae los datos de una receta de HelloFresh.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1[data-test-id="recipeDetailFragment.recipe-name"], h1'
        )
        
        # Descripción (HelloFresh suele tener tags descriptivos)
        descripcion = await self._extraer_texto_seguro(
            page,
            '[data-test-id="recipeDetailFragment.recipe-description"], .recipe-description'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '[data-test-id="recipeDetailFragment.recipe-image"] img, .recipe-header img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos - HelloFresh usa formato específico
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '[data-test-id="recipeDetailFragment.cooking-time"], .cooking-time'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '[data-test-id="recipeDetailFragment.servings"], .servings'
        )
        
        # HelloFresh a veces tiene nivel de dificultad en lugar de tiempo de prep
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '[data-test-id="recipeDetailFragment.preparation-time"], .prep-time'
        )
        
        return RecetaScraped(
            titulo=titulo or "Sin título",
            url_origen=url,
            sitio_origen=self.nombre_sitio,
            descripcion=descripcion,
            imagen_url=imagen_url,
            ingredientes=ingredientes,
            pasos=pasos,
            tiempo_preparacion=tiempo_preparacion,
            tiempo_coccion=tiempo_coccion,
            porciones=porciones
        )
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """Extrae la lista de ingredientes."""
        selectores = [
            '[data-test-id="recipeDetailFragment.ingredient-item"]',
            '.recipe-ingredients li',
            '[class*="ingredient"] li',
            '.ingredients-list li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """Extrae los pasos de preparación."""
        selectores = [
            '[data-test-id="recipeDetailFragment.instructions.step"]',
            '.recipe-steps li',
            '[class*="instruction"] li',
            '.instructions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
