"""
Scraper para Recetas de Rechupete (recetasderechupete.com).

Blog de cocina española con recetas tradicionales.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class RechupeteScraper(BaseScraper):
    """
    Scraper especializado para Recetas de Rechupete.
    
    Extrae recetas del sitio recetasderechupete.com.
    """
    
    nombre_sitio = "Recetas de Rechupete"
    dominios_soportados = ["recetasderechupete.com"]
    
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        """
        Extrae los datos de una receta de Rechupete.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1.entry-title, h1.post-title, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '.entry-content > p:first-of-type, .recipe-summary'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '.entry-content img, .post-thumbnail img, article img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.recipe-prep-time, [class*="tiempo-prep"]'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.recipe-cook-time, [class*="tiempo-coccion"]'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.recipe-servings, [class*="raciones"]'
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
            '.wprm-recipe-ingredient',
            '.recipe-ingredients li',
            '[class*="ingredientes"] li',
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
            '.wprm-recipe-instruction',
            '.recipe-instructions li',
            '[class*="elaboracion"] li',
            '.instructions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
