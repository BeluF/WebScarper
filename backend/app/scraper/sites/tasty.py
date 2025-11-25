"""
Scraper para Tasty (tasty.co).

Plataforma de videos y recetas de BuzzFeed.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class TastyScraper(BaseScraper):
    """
    Scraper especializado para Tasty.
    
    Extrae recetas del sitio tasty.co.
    """
    
    nombre_sitio = "Tasty"
    dominios_soportados = ["tasty.co"]
    
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
