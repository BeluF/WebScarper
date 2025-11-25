"""
Scraper para HelloFresh (hellofresh.com).

Servicio de kits de comida con recetas detalladas.
"""

from typing import List
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class HelloFreshScraper(BaseScraper):
    """
    Scraper especializado para HelloFresh.
    
    Extrae recetas del sitio hellofresh.com.
    """
    
    nombre_sitio = "HelloFresh"
    dominios_soportados = ["hellofresh.com", "hellofresh.es", "hellofresh.com.ar"]
    
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
