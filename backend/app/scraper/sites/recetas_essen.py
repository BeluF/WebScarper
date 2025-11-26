"""
Scraper para Recetas Essen (recetasessen.com.ar).

Sitio de recetas argentino de la marca Essen Argentina (ollas y sartenes).
Es un sitio WordPress con tema personalizado para la marca.
"""

from typing import List, Optional
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class RecetasEssenScraper(BaseScraper):
    """
    Scraper especializado para Recetas Essen.
    
    Extrae recetas del sitio recetasessen.com.ar.
    Maneja estructuras específicas de sitios de marcas y WordPress.
    """
    
    nombre_sitio = "Recetas Essen"
    dominios_soportados = ["recetasessen.com.ar", "recetasessen.com"]
    
    # Encabezados comunes para ingredientes (español)
    ENCABEZADOS_INGREDIENTES = [
        'ingredientes', 'ingredients', 'lista de ingredientes'
    ]
    
    # Encabezados comunes para pasos/preparación (español)
    ENCABEZADOS_PASOS = [
        'preparación', 'preparacion', 'modo de preparación', 'modo de preparacion',
        'instrucciones', 'elaboración', 'elaboracion', 'pasos', 'procedimiento'
    ]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """Construye la URL de búsqueda para Recetas Essen."""
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://www.recetasessen.com.ar/?s={query}"
        return "https://www.recetasessen.com.ar/recetas/"
    
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
        Extrae los datos de una receta de Essen.
        Maneja lazy loading y contenido dinámico.
        
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
            '.recipe-description, .recipe-summary, .entry-content > p:first-of-type'
        )
        
        # Imagen (con soporte para lazy loading)
        imagen_url = await self._extraer_imagen_lazy(page)
        
        # Ingredientes
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos
        pasos = await self._extraer_pasos(page)
        
        # Metadatos
        tiempo_preparacion = await self._extraer_texto_seguro(
            page,
            '.prep-time, .recipe-prep-time, [class*="tiempo-prep"], .cooking-time'
        )
        
        tiempo_coccion = await self._extraer_texto_seguro(
            page,
            '.cook-time, .recipe-cook-time, [class*="tiempo-coccion"]'
        )
        
        porciones = await self._extraer_texto_seguro(
            page,
            '.servings, .recipe-servings, [class*="porciones"], [class*="rinde"]'
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
    
    async def _extraer_imagen_lazy(self, page) -> str:
        """
        Extrae la URL de la imagen principal, considerando lazy loading.
        
        Busca en múltiples atributos: src, data-src, data-lazy-src, data-original.
        
        Args:
            page: Página de Playwright.
            
        Returns:
            URL de la imagen o cadena vacía.
        """
        selectores_imagen = [
            '.recipe-image img',
            '.wp-post-image',
            '.entry-content img',
            'article img',
            '.post-thumbnail img',
            '.featured-image img'
        ]
        
        atributos_lazy = ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-lazy']
        
        for selector in selectores_imagen:
            try:
                elemento = await page.query_selector(selector)
                if elemento:
                    for atributo in atributos_lazy:
                        valor = await elemento.get_attribute(atributo)
                        if valor and valor.strip() and not valor.startswith('data:'):
                            return valor.strip()
            except Exception:
                continue
        
        return ""
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """
        Extrae la lista de ingredientes.
        
        Estrategia:
        1. Buscar selectores específicos de recetas
        2. Buscar contenido después de encabezado "Ingredientes"
        3. Parsear párrafos con <br> como alternativa
        """
        # Selectores específicos para sitios de marcas y WordPress
        selectores = [
            '.recipe-ingredients li',
            '.ingredients-list li',
            '[class*="ingredientes"] li',
            '.ingredients li',
            'ul.ingredientes li',
            '.wprm-recipe-ingredient',
            '.recipe-content .ingredients li',
            'section.ingredientes li'
        ]
        
        for selector in selectores:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        # Fallback: Buscar contenido después de encabezado "Ingredientes"
        ingredientes = await self._extraer_contenido_por_encabezado(
            page, self.ENCABEZADOS_INGREDIENTES
        )
        if ingredientes:
            return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """
        Extrae los pasos de preparación.
        
        Estrategia:
        1. Buscar selectores específicos de recetas
        2. Buscar contenido después de encabezado "Preparación"
        3. Parsear párrafos con <br> como alternativa
        """
        # Selectores específicos para sitios de marcas y WordPress
        selectores = [
            '.recipe-instructions li',
            '.recipe-directions li',
            '[class*="preparacion"] li',
            '[class*="instrucciones"] li',
            '.instructions li',
            'ol.pasos li',
            '.wprm-recipe-instruction',
            '.wprm-recipe-instruction-text',
            '.recipe-content .steps li',
            'section.preparacion li'
        ]
        
        for selector in selectores:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        # Fallback: Buscar contenido después de encabezado "Preparación"
        pasos = await self._extraer_contenido_por_encabezado(
            page, self.ENCABEZADOS_PASOS
        )
        if pasos:
            return pasos
        
        return []
    
    async def _extraer_contenido_por_encabezado(
        self, 
        page, 
        encabezados: List[str]
    ) -> List[str]:
        """
        Método genérico para extraer contenido basado en encabezados.
        
        Busca encabezados (h2, h3, h4, strong) que coincidan con los términos
        dados y extrae el contenido que les sigue (listas o párrafos con <br>).
        
        Args:
            page: Página de Playwright.
            encabezados: Lista de términos a buscar en encabezados.
            
        Returns:
            Lista de textos extraídos.
        """
        items = []
        
        # Buscar en encabezados h2, h3, h4, h5 y elementos strong
        selectores_encabezado = ['h2', 'h3', 'h4', 'h5', 'strong', '.section-title']
        
        for selector in selectores_encabezado:
            try:
                elementos = await page.query_selector_all(selector)
                for elemento in elementos:
                    texto_encabezado = (await elemento.inner_text()).strip().lower()
                    
                    # Verificar si el encabezado coincide con alguno de los buscados
                    if any(enc in texto_encabezado for enc in encabezados):
                        # Buscar contenido siguiente: lista ul/ol o párrafos
                        contenido = await self._extraer_contenido_siguiente(page, elemento)
                        if contenido:
                            return contenido
            except Exception:
                continue
        
        return items
    
    async def _extraer_contenido_siguiente(self, page, elemento_encabezado) -> List[str]:
        """
        Extrae el contenido que sigue a un encabezado.
        
        Busca:
        1. Lista ul/ol siguiente con items li
        2. Párrafos con texto separado por <br>
        3. Divs con contenido de texto
        
        Args:
            page: Página de Playwright.
            elemento_encabezado: Elemento del encabezado encontrado.
            
        Returns:
            Lista de textos extraídos.
        """
        items = []
        
        try:
            # Intentar obtener el siguiente elemento hermano
            siguiente = await page.evaluate('''(el) => {
                let sibling = el.nextElementSibling;
                // Buscar el primer elemento significativo
                while (sibling && sibling.tagName && 
                       ['BR', 'HR'].includes(sibling.tagName.toUpperCase())) {
                    sibling = sibling.nextElementSibling;
                }
                if (!sibling) {
                    // Buscar en el padre
                    const parent = el.parentElement;
                    if (parent) {
                        sibling = parent.nextElementSibling;
                    }
                }
                return sibling ? sibling.outerHTML : null;
            }''', elemento_encabezado)
            
            if siguiente:
                # Parsear el HTML del siguiente elemento
                items = await self._parsear_contenido_html(page, siguiente)
        except Exception:
            pass
        
        return items
    
    async def _parsear_contenido_html(self, page, html: str) -> List[str]:
        """
        Parsea contenido HTML para extraer items.
        
        Maneja:
        - Listas ul/ol con items li
        - Párrafos con texto separado por <br>
        - Texto plano separado por saltos de línea
        
        Args:
            page: Página de Playwright.
            html: Contenido HTML a parsear.
            
        Returns:
            Lista de textos extraídos.
        """
        items = []
        
        # JavaScript code to parse HTML and extract items
        js_code = r'''(html) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const items = [];
            
            // Buscar items de lista
            const liItems = doc.querySelectorAll('li');
            if (liItems.length > 0) {
                liItems.forEach(li => {
                    const text = li.textContent.trim();
                    if (text) items.push(text);
                });
                return items;
            }
            
            // Buscar párrafos
            const paragraphs = doc.querySelectorAll('p');
            if (paragraphs.length > 0) {
                paragraphs.forEach(p => {
                    // Reemplazar <br> con saltos de línea
                    const innerHTML = p.innerHTML.replace(/<br\s*\/?>/gi, '\n');
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = innerHTML;
                    const lines = tempDiv.textContent.split('\n');
                    lines.forEach(line => {
                        const text = line.trim();
                        if (text) items.push(text);
                    });
                });
                return items;
            }
            
            // Fallback: texto plano del elemento raíz
            const root = doc.body.firstElementChild;
            if (root) {
                const innerHTML = root.innerHTML.replace(/<br\s*\/?>/gi, '\n');
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = innerHTML;
                const lines = tempDiv.textContent.split('\n');
                lines.forEach(line => {
                    const text = line.trim();
                    if (text) items.push(text);
                });
            }
            
            return items;
        }'''
        
        try:
            resultado = await page.evaluate(js_code, html)
            
            if resultado:
                items = [item for item in resultado if item and item.strip()]
        except Exception:
            pass
        
        return items
