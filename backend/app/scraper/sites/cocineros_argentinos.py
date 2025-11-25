"""
Scraper para Cocineros Argentinos (cocinerosargentinos.com).

Programa de TV argentino con recetas tradicionales.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class CocinerosArgentinosScraper(BaseScraper):
    """
    Scraper especializado para Cocineros Argentinos.
    
    Extrae recetas del sitio cocinerosargentinos.com.
    """
    
    nombre_sitio = "Cocineros Argentinos"
    dominios_soportados = ["cocinerosargentinos.com"]
    
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
