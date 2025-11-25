"""
Scraper para AllRecipes (allrecipes.com).

Sitio internacional de recetas con versión en español.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class AllRecipesScraper(BaseScraper):
    """
    Scraper especializado para AllRecipes.
    
    Extrae recetas del sitio allrecipes.com.
    """
    
    nombre_sitio = "AllRecipes"
    dominios_soportados = ["allrecipes.com"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """Construye la URL de búsqueda para AllRecipes."""
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://www.allrecipes.com/search?q={query}"
        return "https://www.allrecipes.com/recipes/"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """Extrae la lista de recetas de la página de búsqueda."""
        recetas = []
        selectores = ['a[href*="/recipe/"]', '.card__title-link', '.mntl-card-list-items a']
        
        for selector in selectores:
            try:
                elementos = await page.query_selector_all(selector)
                for elemento in elementos[:limite]:
                    try:
                        href = await elemento.get_attribute("href")
                        if not href or "/recipe/" not in href:
                            continue
                        titulo_elem = await elemento.query_selector('.card__title, span')
                        titulo = ""
                        if titulo_elem:
                            titulo = (await titulo_elem.inner_text()).strip()
                        else:
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
        Extrae los datos de una receta de AllRecipes.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1.article-heading, h1.headline, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '.article-subheading, .recipe-summary p, .article-body p:first-of-type'
        )
        
        # Imagen
        imagen_url = await self._extraer_atributo_seguro(
            page,
            '.primary-image img, .recipe-image img, article img',
            'src'
        )
        
        # Si no hay src, intentar data-src
        if not imagen_url:
            imagen_url = await self._extraer_atributo_seguro(
                page,
                '.primary-image img, .recipe-image img',
                'data-src'
            )
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.recipe-prep-time .meta-value, [class*="prep-time"] .mntl-recipe-details__value'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.recipe-cook-time .meta-value, [class*="cook-time"] .mntl-recipe-details__value'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.recipe-servings .meta-value, [class*="servings"] .mntl-recipe-details__value'
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
            '.mntl-structured-ingredients__list-item',
            '.ingredients-item-name',
            '.recipe-ingredients li',
            '[class*="ingredient"] li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """Extrae los pasos de preparación."""
        selectores = [
            '.mntl-sc-block-group--LI p',
            '.instructions-section-item .paragraph',
            '.recipe-directions__list li',
            '[class*="directions"] li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
