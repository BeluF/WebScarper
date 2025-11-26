"""
Scraper para Cocineros Argentinos (cocinerosargentinos.com).

Programa de TV argentino con recetas tradicionales.
Soporta WordPress con estructuras personalizadas típicas de medios argentinos.
"""

import re
from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class CocinerosArgentinosScraper(BaseScraper):
    """
    Scraper especializado para Cocineros Argentinos.
    
    Extrae recetas del sitio cocinerosargentinos.com.
    Maneja múltiples formatos de contenido incluyendo:
    - Listas HTML (ul/ol)
    - Párrafos con separadores <br>
    - Contenido extraído por encabezados (h2/h3)
    """
    
    nombre_sitio = "Cocineros Argentinos"
    dominios_soportados = ["cocinerosargentinos.com"]
    
    # Títulos que identifican la sección de ingredientes
    TITULOS_INGREDIENTES = ["ingredientes", "ingrediente"]
    # Títulos que identifican la sección de pasos/preparación
    TITULOS_PASOS = ["preparación", "preparacion", "procedimiento", "elaboración", "elaboracion", "pasos"]
    
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
        Maneja lazy loading y diferentes estructuras de contenido.
        
        Args:
            page: Página de Playwright con el contenido.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        self._log(f"Iniciando extracción de: {url}")
        
        # Esperar a que el contenido dinámico cargue
        await self._esperar_contenido_cargado(page)
        
        # Hacer scroll para cargar contenido lazy
        await self._hacer_scroll_para_lazy_loading(page, scrolls=5, delay_ms=500)
        
        # Título
        titulo = await self._extraer_texto_seguro(
            page, 
            'h1.recipe-title, h1.entry-title, h1.post-title, h1'
        )
        
        # Descripción
        descripcion = await self._extraer_texto_seguro(
            page,
            '.recipe-description, .entry-content > p:first-of-type, .post-excerpt'
        )
        
        # Imagen (con soporte para lazy loading)
        imagen_url = await self._extraer_imagen(page)
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.prep-time, [class*="tiempo-prep"], .recipe-prep-time'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.cook-time, [class*="tiempo-coccion"], .recipe-cook-time'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.servings, [class*="porciones"], .recipe-servings'
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
            tiempo_preparacion=tiempo_preparacion,
            tiempo_coccion=tiempo_coccion,
            porciones=porciones
        )
    
    async def _extraer_imagen(self, page) -> str:
        """
        Extrae la URL de la imagen de la receta.
        Soporta lazy loading (data-src, data-lazy-src) y múltiples selectores.
        
        Args:
            page: Página de Playwright.
            
        Returns:
            URL de la imagen o cadena vacía.
        """
        selectores_imagen = [
            '.post-thumbnail img',
            '.featured-image img',
            'figure.wp-block-image img',
            '.wp-post-image',
            '.recipe-image img',
            '.entry-content img',
            'article img'
        ]
        
        atributos_imagen = ['src', 'data-src', 'data-lazy-src', 'data-original']
        
        for selector in selectores_imagen:
            for atributo in atributos_imagen:
                imagen_url = await self._extraer_atributo_seguro(page, selector, atributo)
                if imagen_url and imagen_url.startswith('http'):
                    return imagen_url
        
        return ""
    
    async def _extraer_contenido_por_encabezado(
        self, 
        page, 
        titulos_buscar: List[str]
    ) -> List[str]:
        """
        Extrae contenido que sigue a un encabezado específico (h2, h3).
        Busca el encabezado por texto y extrae la lista o párrafo siguiente.
        
        Args:
            page: Página de Playwright.
            titulos_buscar: Lista de títulos a buscar (case insensitive).
            
        Returns:
            Lista de textos extraídos.
        """
        resultado = []
        
        try:
            # Buscar en encabezados h2 y h3
            for nivel in ['h2', 'h3']:
                encabezados = await page.query_selector_all(nivel)
                for encabezado in encabezados:
                    texto_encabezado = (await encabezado.inner_text()).strip().lower()
                    
                    # Verificar si el encabezado coincide con alguno de los títulos buscados
                    if any(titulo in texto_encabezado for titulo in titulos_buscar):
                        # Buscar el siguiente elemento hermano
                        siguiente = await encabezado.evaluate_handle(
                            '(el) => el.nextElementSibling'
                        )
                        if siguiente:
                            elemento_siguiente = siguiente.as_element()
                            if elemento_siguiente:
                                # Intentar extraer de lista ul/ol
                                items_lista = await elemento_siguiente.query_selector_all('li')
                                if items_lista:
                                    for item in items_lista:
                                        texto = (await item.inner_text()).strip()
                                        if texto:
                                            resultado.append(texto)
                                    if resultado:
                                        return resultado
                                
                                # Si no hay lista, extraer texto del párrafo
                                contenido = await elemento_siguiente.inner_html()
                                if contenido:
                                    resultado = self._parsear_contenido_con_br(contenido)
                                    if resultado:
                                        return resultado
                        
                        # Si nextElementSibling no funcionó, buscar ul/ol/p inmediatamente después
                        # Escapar comillas en el texto para uso seguro en selectores
                        texto_escapado = texto_encabezado.replace('"', '\\"').replace("'", "\\'")
                        for siguiente_tag in ['ul', 'ol', 'p', 'div']:
                            selector_siguiente = f'{nivel}:has-text("{texto_escapado}") + {siguiente_tag}'
                            try:
                                elemento = await page.query_selector(selector_siguiente)
                                if elemento:
                                    if siguiente_tag in ['ul', 'ol']:
                                        items = await elemento.query_selector_all('li')
                                        for item in items:
                                            texto = (await item.inner_text()).strip()
                                            if texto:
                                                resultado.append(texto)
                                    else:
                                        contenido = await elemento.inner_html()
                                        resultado = self._parsear_contenido_con_br(contenido)
                                    
                                    if resultado:
                                        return resultado
                            except Exception:
                                continue
        except Exception:
            pass
        
        return resultado
    
    def _parsear_contenido_con_br(self, html_contenido: str) -> List[str]:
        """
        Parsea contenido HTML que usa <br> como separador de líneas.
        
        Args:
            html_contenido: HTML con posibles tags <br>.
            
        Returns:
            Lista de líneas de texto limpias.
        """
        # Reemplazar variantes de <br>
        texto = re.sub(r'<br\s*/?>', '\n', html_contenido, flags=re.IGNORECASE)
        # Eliminar otros tags HTML
        texto = re.sub(r'<[^>]+>', '', texto)
        # Dividir por saltos de línea y limpiar
        lineas = texto.split('\n')
        resultado = []
        for linea in lineas:
            linea_limpia = linea.strip()
            # Filtrar líneas vacías y muy cortas (probablemente basura)
            if linea_limpia and len(linea_limpia) > 2:
                resultado.append(linea_limpia)
        
        return resultado
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """
        Extrae la lista de ingredientes.
        Intenta múltiples estrategias:
        1. Selectores CSS específicos
        2. Búsqueda por encabezado "Ingredientes"
        3. Contenido genérico de WordPress
        """
        # Estrategia 1: Selectores específicos de recetas
        selectores = [
            '.recipe-ingredients li',
            '.receta-ingredientes li',
            '[class*="ingredientes"] li',
            '.wprm-recipe-ingredient',
            '.ingredients-list li',
            'ul.ingredients li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        # Estrategia 2: Buscar por encabezado
        ingredientes = await self._extraer_contenido_por_encabezado(
            page, self.TITULOS_INGREDIENTES
        )
        if ingredientes:
            return ingredientes
        
        # Estrategia 3: Contenido genérico de WordPress (entry-content)
        selectores_fallback = [
            '.entry-content ul:first-of-type li',
            '.post-content ul:first-of-type li'
        ]
        
        for selector in selectores_fallback:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """
        Extrae los pasos de preparación.
        Intenta múltiples estrategias:
        1. Selectores CSS específicos
        2. Búsqueda por encabezado "Preparación"/"Procedimiento"
        3. Listas ordenadas genéricas
        """
        # Estrategia 1: Selectores específicos de recetas
        selectores = [
            '.recipe-directions li',
            '.recipe-instructions li',
            '.receta-preparacion li',
            '[class*="preparacion"] li',
            '[class*="procedimiento"] li',
            '[class*="elaboracion"] li',
            '.wprm-recipe-instruction',
            '.recipe-steps li',
            'ol.directions li',
            'ol.instructions li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        # Estrategia 2: Buscar por encabezado
        pasos = await self._extraer_contenido_por_encabezado(
            page, self.TITULOS_PASOS
        )
        if pasos:
            return pasos
        
        # Estrategia 3: Listas ordenadas genéricas
        selectores_fallback = [
            '.entry-content ol li',
            '.post-content ol li'
        ]
        
        for selector in selectores_fallback:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
