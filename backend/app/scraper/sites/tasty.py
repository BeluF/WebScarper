"""
Scraper para Tasty (tasty.co).

Plataforma de videos y recetas de BuzzFeed.
NOTA: Tasty está principalmente en inglés, pero intentamos filtrar contenido en español.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class TastyScraper(BaseScraper):
    """
    Scraper especializado para Tasty.
    
    Extrae recetas del sitio tasty.co.
    ADVERTENCIA: La mayoría del contenido está en inglés.
    Las recetas en inglés serán descartadas por la validación de idioma.
    """
    
    nombre_sitio = "Tasty"
    dominios_soportados = ["tasty.co"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """
        Construye la URL de búsqueda para Tasty.
        
        Intentamos buscar con términos en español para mejorar
        las probabilidades de encontrar contenido en español.
        """
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://tasty.co/search?q={query}"
        # Buscar recetas con términos en español como fallback
        return "https://tasty.co/search?q=receta"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """Extrae la lista de recetas de la página de búsqueda."""
        recetas = []
        selectores = ['a[href*="/recipe/"]', '.feed-item a']
        
        for selector in selectores:
            try:
                elementos = await page.query_selector_all(selector)
                for elemento in elementos[:limite]:
                    try:
                        href = await elemento.get_attribute("href")
                        if not href or "/recipe/" not in href:
                            continue
                        if href.startswith("/"):
                            href = f"https://tasty.co{href}"
                        titulo_elem = await elemento.query_selector('h3, .feed-item__title')
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
        Extrae los datos de una receta de Tasty.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1[class*="recipe-name"], h1.recipe-title, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '[class*="recipe-description"], .recipe-description'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '.recipe-photo img, picture img, [class*="recipe-image"] img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos - Tasty usa formato específico
        porciones = await self._extraer_texto_seguro(
            page,
            '[class*="servings"], .servings-display'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '[class*="cook-time"], .total-time'
        )
        
        return RecetaScraped(
            titulo=titulo or "Sin título",
            url_origen=url,
            sitio_origen=self.nombre_sitio,
            descripcion=descripcion,
            imagen_url=imagen_url,
            ingredientes=ingredientes,
            pasos=pasos,
            tiempo_coccion=tiempo_coccion,
            porciones=porciones
        )
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """Extrae la lista de ingredientes."""
        selectores = [
            '[class*="ingredient-list"] li',
            '.ingredient-list li',
            '[class*="ingredients"] li',
            '.ingredients li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """Extrae los pasos de preparación."""
        selectores = [
            '[class*="preparation-list"] li',
            '.preparation-list li',
            '[class*="instructions"] li',
            '.instructions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
