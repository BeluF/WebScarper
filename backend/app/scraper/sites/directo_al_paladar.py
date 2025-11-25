"""
Scraper para Directo al Paladar (directoalpaladar.com).

Blog de recetas español con amplia variedad de platos.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class DirectoAlPaladarScraper(BaseScraper):
    """
    Scraper especializado para Directo al Paladar.
    
    Extrae recetas del blog directoalpaladar.com.
    """
    
    nombre_sitio = "Directo al Paladar"
    dominios_soportados = ["directoalpaladar.com"]
    
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        """
        Extrae los datos de una receta de Directo al Paladar.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1.title, h1.article-title, h1'
        )
        
        # Descripción - primer párrafo del artículo
        descripcion = await self._extraer_texto_seguro(
            page,
            '.article-content p:first-of-type, .recipe-intro'
        )
        
        # Imagen principal
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '.article-image img, .featured-image img, article img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Tiempo y porciones
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.recipe-prep-time, [class*="prep-time"]'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.recipe-cook-time, [class*="cook-time"]'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.recipe-servings, [class*="servings"], [class*="comensales"]'
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
            '[class*="elaboracion"] li',
            '.recipe-steps li',
            'ol.directions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
