"""
Scraper para Cookpad (cookpad.com).

Cookpad es una comunidad de recetas donde usuarios comparten sus creaciones.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class CookpadScraper(BaseScraper):
    """
    Scraper especializado para el sitio Cookpad.
    
    Extrae recetas del sitio cookpad.com incluyendo
    ingredientes, pasos e información nutricional.
    """
    
    nombre_sitio = "Cookpad"
    dominios_soportados = ["cookpad.com"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """
        Construye la URL de búsqueda para Cookpad.
        
        Args:
            palabra_clave: Texto a buscar.
            filtros: Filtros dietéticos a aplicar.
            
        Returns:
            URL de búsqueda de Cookpad.
        """
        base_url = "https://cookpad.com/ar/buscar"
        
        if palabra_clave:
            # Agregar palabra clave
            query = quote(palabra_clave)
            return f"{base_url}/{query}"
        
        # Si no hay palabra clave, buscar recetas populares
        return "https://cookpad.com/ar/buscar/populares"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """Extrae la lista de recetas de la página de búsqueda."""
        recetas = []
        
        # Selectores para las tarjetas de recetas en Cookpad
        selectores_tarjeta = [
            'a[href*="/recetas/"]',
            '.recipe-preview a',
            '[class*="recipe-card"] a',
            'article a'
        ]
        
        for selector in selectores_tarjeta:
            try:
                elementos = await page.query_selector_all(selector)
                
                for elemento in elementos[:limite]:
                    try:
                        href = await elemento.get_attribute("href")
                        if not href or "/recetas/" not in href:
                            continue
                        
                        # Asegurar URL completa
                        if href.startswith("/"):
                            href = f"https://cookpad.com{href}"
                        
                        # Extraer título
                        titulo_elem = await elemento.query_selector("h2, h3, .recipe-title, [class*='title']")
                        titulo = ""
                        if titulo_elem:
                            titulo = (await titulo_elem.inner_text()).strip()
                        
                        # Extraer imagen
                        img_elem = await elemento.query_selector("img")
                        imagen = ""
                        if img_elem:
                            imagen = await img_elem.get_attribute("src") or ""
                        
                        if href:
                            recetas.append({
                                "url": href,
                                "titulo": titulo,
                                "imagen_preview": imagen
                            })
                            
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
        Extrae los datos de una receta de Cookpad.
        Algunas recetas cargan ingredientes dinámicamente.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        self._log(f"Iniciando extracción de: {url}")
        
        # Esperar a que el contenido dinámico cargue
        await self._esperar_contenido_cargado(page)
        
        # Selectores específicos de Cookpad para ingredientes
        selectores_ingredientes = [
            '#ingredients',
            '#ingredients .ingredient',
            '[data-ingredient-id]',
            '[class*="ingredient-list"]',
            '.ingredient-list li',
            '#ingredients li'
        ]
        
        # Selectores específicos de Cookpad para pasos
        selectores_pasos = [
            '#steps',
            '#steps .step',
            '[data-step-number]',
            '[class*="step-text"]',
            '.step-text',
            '#steps li'
        ]
        
        # Esperar al menos uno de los selectores de ingredientes
        selector_ing = await self._esperar_cualquier_selector(
            page, selectores_ingredientes, timeout=15000
        )
        if not selector_ing:
            self._log("⚠️ No se encontraron selectores de ingredientes")
        
        # Esperar al menos uno de los selectores de pasos
        selector_pasos = await self._esperar_cualquier_selector(
            page, selectores_pasos, timeout=15000
        )
        if not selector_pasos:
            self._log("⚠️ No se encontraron selectores de pasos")
        
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
        
        # Imagen - buscar src y data-src para lazy loading
        imagen_url = await self._extraer_imagen_con_lazy_loading(page)
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Información adicional - selectores más específicos
        porciones = await self._extraer_texto_seguro(
            page,
            '#servings, .serving-size, [class*="serving"], .servings'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '#cooking-time, [class*="cooking-time"], .cooking-time'
        )
        
        self._log(f"✅ Receta extraída: {titulo}")
        
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
    
    async def _extraer_imagen_con_lazy_loading(self, page) -> str:
        """
        Extrae la URL de la imagen, soportando lazy loading (data-src).
        
        Args:
            page: Página de Playwright.
            
        Returns:
            URL de la imagen o cadena vacía.
        """
        selectores_imagen = [
            '#recipe-image img',
            '.recipe-image img',
            'picture img',
            'img[class*="recipe-image"]',
            '.recipe-main-photo img'
        ]
        
        for selector in selectores_imagen:
            try:
                elemento = await page.query_selector(selector)
                if elemento:
                    # Primero intentar data-src (lazy loading)
                    data_src = await elemento.get_attribute('data-src')
                    if data_src and data_src.strip():
                        return data_src.strip()
                    # Si no hay data-src, usar src
                    src = await elemento.get_attribute('src')
                    if src and src.strip():
                        return src.strip()
            except Exception:
                continue
        
        return ""
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """
        Extrae la lista de ingredientes.
        Combina cantidad + nombre cuando están separados.
        """
        # Selectores para ingredientes con cantidad y nombre separados
        selectores_combinados = [
            ('#ingredients li', '.ingredient-quantity', '.ingredient-name'),
            ('.ingredient-list li', '.ingredient-quantity', '.ingredient-name'),
            ('[data-ingredient-id]', '.ingredient-quantity', '.ingredient-name'),
            ('.ingredient', '.ingredient-quantity', '.ingredient-name'),
        ]
        
        # Intentar extraer con cantidad y nombre separados
        for contenedor, sel_cantidad, sel_nombre in selectores_combinados:
            try:
                elementos = await page.query_selector_all(contenedor)
                if elementos:
                    ingredientes = []
                    for elemento in elementos:
                        cantidad_elem = await elemento.query_selector(sel_cantidad)
                        nombre_elem = await elemento.query_selector(sel_nombre)
                        
                        cantidad = ""
                        nombre = ""
                        
                        if cantidad_elem:
                            cantidad = (await cantidad_elem.inner_text()).strip()
                        if nombre_elem:
                            nombre = (await nombre_elem.inner_text()).strip()
                        
                        # Combinar cantidad + nombre
                        if cantidad and nombre:
                            ingredientes.append(f"{cantidad} {nombre}")
                        elif nombre:
                            ingredientes.append(nombre)
                        elif cantidad:
                            ingredientes.append(cantidad)
                        else:
                            # Fallback: usar texto completo del elemento
                            texto = (await elemento.inner_text()).strip()
                            if texto:
                                ingredientes.append(texto)
                    
                    if ingredientes:
                        return ingredientes
            except Exception:
                continue
        
        # Fallback: selectores simples sin separación
        selectores = [
            '[data-ingredient-id]',
            '#ingredients .ingredient',
            '[class*="ingredient-list"] li',
            '.ingredient-list li',
            '#ingredients li',
            '#ingredients div'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """
        Extrae los pasos de preparación.
        Solo extrae el texto del paso, no las imágenes.
        """
        # Selectores para pasos con estructura específica
        selectores_con_texto = [
            ('#steps li', '.step-text'),
            ('[data-step-number]', '.step-text'),
            ('.step', '.step-text'),
            ('#steps .step', '.step-text'),
        ]
        
        # Intentar extraer solo el texto del paso
        for contenedor, sel_texto in selectores_con_texto:
            try:
                elementos = await page.query_selector_all(contenedor)
                if elementos:
                    pasos = []
                    for elemento in elementos:
                        texto_elem = await elemento.query_selector(sel_texto)
                        if texto_elem:
                            texto = (await texto_elem.inner_text()).strip()
                            if texto:
                                pasos.append(texto)
                        else:
                            # Fallback: usar texto completo pero ignorar imágenes
                            texto = (await elemento.inner_text()).strip()
                            if texto:
                                pasos.append(texto)
                    
                    if pasos:
                        return pasos
            except Exception:
                continue
        
        # Fallback: selectores simples
        selectores = [
            '[data-step-number]',
            '#steps .step',
            '.step-text',
            '[class*="step-text"]',
            '#steps li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
