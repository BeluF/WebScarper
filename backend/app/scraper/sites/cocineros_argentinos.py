"""
Scraper para Cocineros Argentinos (cocinerosargentinos.com).

Programa de TV argentino con recetas tradicionales.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class CocinerosArgentinosScraper(BaseScraper):
    """
    Scraper especializado para Cocineros Argentinos.
    
    Extrae recetas del sitio cocinerosargentinos.com.
    """
    
    nombre_sitio = "Cocineros Argentinos"
    dominios_soportados = ["cocinerosargentinos.com"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """Construye la URL de búsqueda para Cocineros Argentinos."""
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://www.cocinerosargentinos.com/?s={query}"
        return "https://www.cocinerosargentinos.com/recetas/"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """Extrae la lista de recetas de la página de búsqueda."""
        recetas = []
        selectores = ['article a', '.entry-title a', 'a[href*="receta"]']
        
        for selector in selectores:
            try:
                elementos = await page.query_selector_all(selector)
                for elemento in elementos[:limite]:
                    try:
                        href = await elemento.get_attribute("href")
                        if not href:
                            continue
                        titulo = (await elemento.inner_text()).strip()
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
        Extrae los datos de una receta de Cocineros Argentinos.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1.recipe-title, h1.entry-title, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '.recipe-description, .entry-content > p:first-of-type'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '.recipe-image img, .featured-image img, article img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.prep-time, [class*="tiempo-prep"]'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.cook-time, [class*="tiempo-coccion"]'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.servings, [class*="porciones"]'
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
            '.recipe-ingredients li',
            '[class*="ingredientes"] li',
            '.ingredients-list li',
            'ul.ingredients li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """Extrae los pasos de preparación."""
        selectores = [
            '.recipe-directions li',
            '[class*="preparacion"] li',
            '.recipe-steps li',
            'ol.directions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
