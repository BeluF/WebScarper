"""
Scraper para Soy Celíaco No Extraterrestre (soyceliaconoextraterrestre.com).

Blog especializado en recetas sin gluten/sin TACC.
"""

import re
from typing import List, Optional, Tuple
from urllib.parse import quote
from app.scraper.base_scraper import BaseScraper, RecetaScraped


class SoyCeliacoScraper(BaseScraper):
    """
    Scraper especializado para Soy Celíaco No Extraterrestre.
    
    Extrae recetas sin gluten del sitio.
    
    Estructura del sitio:
    - Ingredientes: en un <p> después de <h2> con "Ingredientes", separados por <br>
    - Pasos: múltiples <h4> + <p> después de <h2> con "paso a paso"
    - Metadatos: en el primer párrafo (porciones, tiempo de preparación, tiempo de cocción)
    - Imágenes: pueden usar lazy loading con data-src
    """
    
    nombre_sitio = "Soy Celíaco No Extraterrestre"
    dominios_soportados = ["soyceliaconoextraterrestre.com"]
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """Construye la URL de búsqueda para Soy Celíaco."""
        if palabra_clave:
            query = quote(palabra_clave)
            return f"https://www.soyceliaconoextraterrestre.com/?s={query}"
        return "https://www.soyceliaconoextraterrestre.com/recetas/"
    
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
                        titulo = (await elemento.inner_text()).strip() if elemento else ""
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
        Extrae los datos de una receta sin gluten.
        
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
            '.entry-content > p:first-of-type, .recipe-description'
        )
        
        # Imagen (con soporte para lazy loading)
        imagen_url = await self._extraer_imagen_con_lazy_loading(page)
        
        # Ingredientes (desde párrafo con <br>)
        ingredientes = await self._extraer_ingredientes(page)
        
        # Pasos (desde secciones <h4> + <p>)
        pasos = await self._extraer_pasos(page)
        
        # Metadatos (desde el primer párrafo)
        tiempo_preparacion, tiempo_coccion, porciones = await self._extraer_metadatos(page)
        
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
    
    async def _extraer_imagen_con_lazy_loading(self, page) -> str:
        """
        Extrae la URL de la imagen, soportando lazy loading.
        
        Busca primero en data-src (lazy loading), luego en src.
        
        Args:
            page: Página de Playwright.
            
        Returns:
            URL de la imagen o string vacío.
        """
        selectores = [
            '.wp-block-image img',
            'figure.wp-block-image img',
            '.wp-post-image',
            '.entry-content img',
            '.post-thumbnail img'
        ]
        
        for selector in selectores:
            try:
                elemento = await page.query_selector(selector)
                if elemento:
                    # Intentar data-src primero (lazy loading)
                    data_src = await elemento.get_attribute('data-src')
                    if data_src and data_src.strip():
                        return data_src.strip()
                    # Luego intentar src
                    src = await elemento.get_attribute('src')
                    if src and src.strip():
                        return src.strip()
            except Exception:
                continue
        
        return ""
    
    async def _extraer_ingredientes(self, page) -> List[str]:
        """
        Extrae la lista de ingredientes.
        
        Busca un <h2> que contenga "Ingredientes" (case insensitive),
        luego obtiene el siguiente elemento <p> hermano y divide
        el contenido por <br> para obtener cada ingrediente.
        
        Args:
            page: Página de Playwright.
            
        Returns:
            Lista de ingredientes.
        """
        try:
            # Buscar h2 que contenga "Ingredientes"
            ingredientes = await page.evaluate('''() => {
                const h2Elements = document.querySelectorAll('h2');
                for (const h2 of h2Elements) {
                    if (h2.textContent.toLowerCase().includes('ingredientes')) {
                        // Buscar el siguiente elemento <p> hermano
                        let sibling = h2.nextElementSibling;
                        while (sibling) {
                            if (sibling.tagName.toLowerCase() === 'p') {
                                // Obtener el HTML interno y dividir por <br>
                                const html = sibling.innerHTML;
                                const items = html.split(/<br\\s*\\/?>/gi)
                                    .map(item => {
                                        // Crear elemento temporal para obtener texto
                                        const temp = document.createElement('div');
                                        temp.innerHTML = item;
                                        return temp.textContent.trim();
                                    })
                                    .filter(item => item.length > 0);
                                if (items.length > 0) {
                                    return items;
                                }
                            }
                            sibling = sibling.nextElementSibling;
                        }
                    }
                }
                return [];
            }''')
            
            if ingredientes:
                return ingredientes
        except Exception:
            pass
        
        # Fallback: intentar selectores tradicionales
        selectores_fallback = [
            '.wprm-recipe-ingredient',
            '.recipe-ingredients li',
            '[class*="ingredientes"] li',
            '.entry-content ul li'
        ]
        
        for selector in selectores_fallback:
            ingredientes = await self._extraer_lista_textos(page, selector)
            if ingredientes:
                return ingredientes
        
        return []
    
    async def _extraer_pasos(self, page) -> List[str]:
        """
        Extrae los pasos de preparación.
        
        Busca un <h2> que contenga "paso a paso" (case insensitive),
        luego extrae todos los <h4> y sus párrafos <p> siguientes
        para formar cada paso combinando el título con el contenido.
        
        Args:
            page: Página de Playwright.
            
        Returns:
            Lista de pasos de preparación.
        """
        try:
            pasos = await page.evaluate('''() => {
                const h2Elements = document.querySelectorAll('h2');
                let startH2 = null;
                
                // Buscar el h2 con "paso a paso"
                for (const h2 of h2Elements) {
                    if (h2.textContent.toLowerCase().includes('paso a paso')) {
                        startH2 = h2;
                        break;
                    }
                }
                
                if (!startH2) {
                    return [];
                }
                
                const pasos = [];
                let sibling = startH2.nextElementSibling;
                
                // Contenido no relevante a filtrar
                const filtrarContenido = (texto) => {
                    const lower = texto.toLowerCase();
                    // Filtrar links internos, ads, scripts
                    if (lower.includes('publicidad') || 
                        lower.includes('suscribite') ||
                        lower.includes('seguinos') ||
                        lower.includes('compartir') ||
                        lower.includes('facebook') ||
                        lower.includes('instagram') ||
                        lower.includes('twitter') ||
                        lower.includes('pinterest') ||
                        lower.includes('youtube') ||
                        lower.includes('también te puede interesar') ||
                        lower.includes('te puede interesar')) {
                        return true;
                    }
                    return false;
                };
                
                while (sibling) {
                    const tagName = sibling.tagName.toLowerCase();
                    
                    // Detenerse si encontramos otro h2 (nueva sección)
                    if (tagName === 'h2') {
                        break;
                    }
                    
                    // Si es un h4, es el título de un paso
                    if (tagName === 'h4') {
                        const titulo = sibling.textContent.trim();
                        let contenido = '';
                        
                        // Buscar el siguiente <p> para el contenido
                        let nextSibling = sibling.nextElementSibling;
                        while (nextSibling && nextSibling.tagName.toLowerCase() === 'p') {
                            const texto = nextSibling.textContent.trim();
                            if (texto && !filtrarContenido(texto)) {
                                contenido += (contenido ? ' ' : '') + texto;
                            }
                            nextSibling = nextSibling.nextElementSibling;
                            // Solo tomar párrafos consecutivos
                            if (nextSibling && nextSibling.tagName.toLowerCase() !== 'p') {
                                break;
                            }
                        }
                        
                        // Combinar título y contenido
                        if (titulo && contenido && !filtrarContenido(titulo)) {
                            pasos.push(titulo + ': ' + contenido);
                        } else if (contenido && !filtrarContenido(contenido)) {
                            pasos.push(contenido);
                        }
                    }
                    // Si es un párrafo suelto (sin h4 previo), agregarlo directamente
                    else if (tagName === 'p') {
                        const texto = sibling.textContent.trim();
                        // Solo agregar si es contenido relevante
                        if (texto && texto.length > 20 && !filtrarContenido(texto)) {
                            // Verificar que no sea un párrafo que ya procesamos con un h4
                            const prevSibling = sibling.previousElementSibling;
                            if (!prevSibling || prevSibling.tagName.toLowerCase() !== 'h4') {
                                pasos.push(texto);
                            }
                        }
                    }
                    
                    sibling = sibling.nextElementSibling;
                }
                
                return pasos;
            }''')
            
            if pasos:
                return pasos
        except Exception:
            pass
        
        # Fallback: intentar selectores tradicionales
        selectores_fallback = [
            '.wprm-recipe-instruction',
            '.recipe-instructions li',
            '[class*="preparacion"] li',
            '.entry-content ol li'
        ]
        
        for selector in selectores_fallback:
            pasos = await self._extraer_lista_textos(page, selector)
            if pasos:
                return pasos
        
        return []
    
    async def _extraer_metadatos(self, page) -> Tuple[str, str, str]:
        """
        Extrae metadatos de tiempo y porciones.
        
        Busca en el primer párrafo de la página patrones como:
        - "Rinde para X" o "X porciones"
        - "Tiempo de preparación: X"
        - "Tiempo de cocción: X"
        
        Args:
            page: Página de Playwright.
            
        Returns:
            Tupla (tiempo_preparacion, tiempo_coccion, porciones).
        """
        tiempo_preparacion = ""
        tiempo_coccion = ""
        porciones = ""
        
        try:
            # Obtener el primer párrafo del contenido
            primer_parrafo = await page.evaluate('''() => {
                const paragraphs = document.querySelectorAll('.entry-content p');
                for (const p of paragraphs) {
                    const texto = p.textContent.trim();
                    // Buscar párrafos que contengan información de tiempo/porciones
                    if (texto.toLowerCase().includes('rinde') || 
                        texto.toLowerCase().includes('tiempo') ||
                        texto.toLowerCase().includes('porciones') ||
                        texto.toLowerCase().includes('minutos')) {
                        return texto;
                    }
                }
                // Si no encontramos con criterios específicos, retornar el primero
                const firstP = document.querySelector('.entry-content p');
                return firstP ? firstP.textContent.trim() : '';
            }''')
            
            if primer_parrafo:
                # Extraer porciones
                patron_porciones = re.compile(
                    r'(?:rinde\s+(?:para\s+)?(\d+)\s*(?:porciones?|pancitos?|unidades?)?|'
                    r'(\d+)\s*porciones?)',
                    re.IGNORECASE
                )
                match_porciones = patron_porciones.search(primer_parrafo)
                if match_porciones:
                    num = match_porciones.group(1) or match_porciones.group(2)
                    porciones = f"{num} porciones"
                
                # Extraer tiempo de preparación
                patron_prep = re.compile(
                    r'tiempo\s+de\s+preparaci[oó]n[:\s]+(\d+\s*(?:minutos?|min|horas?|h))',
                    re.IGNORECASE
                )
                match_prep = patron_prep.search(primer_parrafo)
                if match_prep:
                    tiempo_preparacion = match_prep.group(1)
                
                # Extraer tiempo de cocción
                patron_coccion = re.compile(
                    r'tiempo\s+de\s+cocci[oó]n[:\s]+(\d+\s*(?:minutos?|min|horas?|h)(?:\s*[^\n<]*)?)',
                    re.IGNORECASE
                )
                match_coccion = patron_coccion.search(primer_parrafo)
                if match_coccion:
                    tiempo_coccion = match_coccion.group(1).strip()
        except Exception:
            pass
        
        return tiempo_preparacion, tiempo_coccion, porciones
