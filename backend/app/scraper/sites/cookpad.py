"""
Scraper para Cookpad (cookpad.com).

Cookpad es una comunidad de recetas donde usuarios comparten sus creaciones.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class CookpadScraper(BaseScraper):
    """
    Scraper especializado para el sitio Cookpad.
    
    Extrae recetas del sitio cookpad.com incluyendo
    ingredientes, pasos e información nutricional.
    """
    
    nombre_sitio = "Cookpad"
    dominios_soportados = ["cookpad.com"]
    
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        """
        Extrae los datos de una receta de Cookpad.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1[class*="recipe-title"], h1.break-words, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '[class*="recipe-story"], .mb-sm'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            'picture img, img[class*="recipe-image"], .recipe-main-photo img',
            'src'
        )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Información adicional
        porciones = await self._extraer_texto_seguro(
            page,
            '[class*="serving"], .servings'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '[class*="cooking-time"], .cooking-time'
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
        # Intentar diferentes selectores
        selectores = [
            '#ingredients .ingredient',
            '[class*="ingredient-list"] li',
            '.ingredient-list li',
            '#ingredients li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """Extrae los pasos de preparación."""
        selectores = [
            '#steps .step',
            '[class*="step-text"]',
            '.step-text',
            '#steps li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
