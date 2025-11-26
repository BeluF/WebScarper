"""
Clase base abstracta para scrapers de recetas.

Define la interfaz común que deben implementar todos los scrapers específicos.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Tuple
import asyncio
import time
import re

from app.config import SCRAPER_TIMEOUT, SCRAPER_HEADLESS, RATE_LIMIT_DELAY


# Constantes para detección de idioma
PALABRAS_ESPANOL = [
    'preparación', 'ingredientes', 'minutos', 'cocinar', 
    'mezclar', 'añadir', 'hervir', 'porciones', 'tiempo',
    'receta', 'preparar', 'agregar', 'cucharada', 'taza',
    'horno', 'fuego', 'sartén', 'olla', 'picar', 'cortar'
]

PALABRAS_INGLES = [
    'preparation', 'ingredients', 'minutes', 'cook', 
    'mix', 'add', 'boil', 'servings', 'time',
    'recipe', 'prepare', 'tablespoon', 'cup',
    'oven', 'heat', 'pan', 'pot', 'chop', 'cut'
]

# Constantes para separación de ingredientes y pasos
# Longitud máxima de texto para considerarse ingrediente con cantidad
LONGITUD_MAX_INGREDIENTE_CON_CANTIDAD = 100
# Longitud mínima para considerarse un paso (texto largo)
LONGITUD_MIN_PASO = 80
# Longitud máxima para considerarse ingrediente corto
LONGITUD_MAX_INGREDIENTE_CORTO = 50

# Verbos comunes en pasos de cocina (español)
VERBOS_COCINA = [
    'mezclar', 'cocinar', 'hornear', 'agregar', 'añadir', 'batir', 
    'freír', 'hervir', 'cortar', 'picar', 'revolver', 'calentar',
    'dejar', 'colocar', 'poner', 'servir', 'decorar', 'reservar',
    'incorporar', 'salpimentar', 'precalentar', 'retirar', 'escurrir'
]


def validar_receta(receta: dict) -> Tuple[bool, str]:
    """
    Valida que una receta tenga los datos mínimos requeridos.
    
    Una receta DEBE tener como mínimo: título, al menos 1 ingrediente, al menos 1 paso.
    
    Args:
        receta: Diccionario con los datos de la receta.
        
    Returns:
        tuple: (es_valida: bool, mensaje_error: str)
    """
    errores = []
    
    # Validar título
    titulo = receta.get('titulo') or ""
    if not titulo or not titulo.strip() or titulo.strip() == "Sin título":
        errores.append("Falta el título")
    
    # Validar ingredientes
    ingredientes = receta.get('ingredientes', [])
    if not ingredientes or len(ingredientes) == 0:
        errores.append("No tiene ingredientes")
    elif all(not ing.strip() for ing in ingredientes if isinstance(ing, str)):
        errores.append("Los ingredientes están vacíos")
    
    # Validar pasos
    pasos = receta.get('pasos', [])
    if not pasos or len(pasos) == 0:
        errores.append("No tiene pasos de preparación")
    elif all(not paso.strip() for paso in pasos if isinstance(paso, str)):
        errores.append("Los pasos están vacíos")
    
    if errores:
        return False, "; ".join(errores)
    return True, ""


def detectar_idioma(texto: str) -> str:
    """
    Detecta si el texto está en español o inglés.
    Usa palabras comunes como indicador.
    
    Args:
        texto: Texto a analizar.
        
    Returns:
        'es' para español, 'en' para inglés, 'desconocido' si no se puede determinar.
    """
    texto_lower = texto.lower()
    
    count_es = sum(1 for p in PALABRAS_ESPANOL if p in texto_lower)
    count_en = sum(1 for p in PALABRAS_INGLES if p in texto_lower)
    
    if count_es > count_en:
        return 'es'
    elif count_en > count_es:
        return 'en'
    return 'desconocido'


def separar_ingredientes_y_pasos(items: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separa una lista mezclada de ingredientes y pasos.
    
    Heurísticas:
    - Ingredientes: cortos, tienen cantidades/unidades
    - Pasos: largos, tienen verbos de acción
    
    Args:
        items: Lista de textos mezclados.
        
    Returns:
        tuple: (ingredientes, pasos)
    """
    # Patrones para detectar ingredientes (incluye unidades métricas comunes)
    patron_cantidad = re.compile(
        r'\d+\s*(g|kg|ml|l|cucharada|cucharadita|taza|unidad|diente|pizca|gramo|kilo|litro|cc)',
        re.IGNORECASE
    )
    
    ingredientes = []
    pasos = []
    
    for item in items:
        if not isinstance(item, str):
            continue
        item = item.strip()
        if not item:
            continue
            
        # Si es corto y tiene cantidad → ingrediente
        if len(item) < LONGITUD_MAX_INGREDIENTE_CON_CANTIDAD and patron_cantidad.search(item):
            ingredientes.append(item)
        # Si es largo o tiene verbos de cocina → paso
        elif len(item) > LONGITUD_MIN_PASO or any(verbo in item.lower() for verbo in VERBOS_COCINA):
            pasos.append(item)
        # Si es muy corto, probablemente ingrediente
        elif len(item) < LONGITUD_MAX_INGREDIENTE_CORTO:
            ingredientes.append(item)
        else:
            pasos.append(item)
    
    return ingredientes, pasos


@dataclass
class RecetaScraped:
    """
    Estructura de datos para una receta scrapeada.
    
    Esta clase representa los datos extraídos de un sitio web
    antes de ser almacenados en la base de datos.
    """
    titulo: str
    url_origen: str
    sitio_origen: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    ingredientes: List[str] = None
    pasos: List[str] = None
    tiempo_preparacion: Optional[str] = None
    tiempo_coccion: Optional[str] = None
    porciones: Optional[str] = None
    
    def __post_init__(self):
        if self.ingredientes is None:
            self.ingredientes = []
        if self.pasos is None:
            self.pasos = []
    
    def validar(self) -> Tuple[bool, str]:
        """
        Valida que la receta tenga los datos mínimos requeridos.
        
        Returns:
            tuple: (es_valida: bool, mensaje_error: str)
        """
        return validar_receta({
            'titulo': self.titulo,
            'ingredientes': self.ingredientes,
            'pasos': self.pasos
        })
    
    def obtener_texto_completo(self) -> str:
        """
        Obtiene todo el texto de la receta para análisis.
        
        Returns:
            str: Texto combinado de título, ingredientes y pasos.
        """
        partes = [self.titulo or ""]
        if self.descripcion:
            partes.append(self.descripcion)
        partes.extend(self.ingredientes or [])
        partes.extend(self.pasos or [])
        return " ".join(partes)
    
    def detectar_idioma(self) -> str:
        """
        Detecta el idioma del contenido de la receta.
        
        Returns:
            str: 'es', 'en' o 'desconocido'
        """
        texto = self.obtener_texto_completo()
        return detectar_idioma(texto)


class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers de sitios de recetas.
    
    Proporciona funcionalidad común como manejo de Playwright,
    rate limiting y configuración de proxy.
    
    Attributes:
        nombre_sitio: Nombre del sitio web que scrapea.
        dominios_soportados: Lista de dominios que puede manejar este scraper.
    """
    
    nombre_sitio: str = "Base"
    dominios_soportados: List[str] = []
    
    def __init__(self, proxy: Optional[str] = None):
        """
        Inicializa el scraper.
        
        Args:
            proxy: URL del proxy a usar (opcional).
        """
        self.proxy = proxy
        self.timeout = SCRAPER_TIMEOUT
        self.headless = SCRAPER_HEADLESS
        self._ultimo_request = 0
    
    @classmethod
    def soporta_url(cls, url: str) -> bool:
        """
        Verifica si este scraper puede manejar la URL dada.
        
        Args:
            url: URL a verificar.
            
        Returns:
            True si el scraper puede manejar la URL.
        """
        url_lower = url.lower()
        return any(dominio in url_lower for dominio in cls.dominios_soportados)
    
    async def _esperar_rate_limit(self):
        """Implementa rate limiting entre peticiones."""
        ahora = time.time()
        tiempo_desde_ultimo = ahora - self._ultimo_request
        if tiempo_desde_ultimo < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - tiempo_desde_ultimo)
        self._ultimo_request = time.time()
    
    async def _crear_contexto_playwright(self, playwright):
        """
        Crea un contexto de navegador con la configuración apropiada.
        
        Args:
            playwright: Instancia de Playwright.
            
        Returns:
            Tuple con el navegador y la página.
        """
        launch_options = {
            "headless": self.headless,
        }
        
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        browser = await playwright.chromium.launch(**launch_options)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        page.set_default_timeout(self.timeout)
        
        return browser, page
    
    async def scrapear(self, url: str) -> RecetaScraped:
        """
        Método principal para scrapear una receta.
        
        Args:
            url: URL de la receta a scrapear.
            
        Returns:
            RecetaScraped con los datos extraídos.
            
        Raises:
            Exception: Si hay un error durante el scraping.
        """
        from playwright.async_api import async_playwright
        
        await self._esperar_rate_limit()
        
        async with async_playwright() as playwright:
            browser, page = await self._crear_contexto_playwright(playwright)
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                # Esperar un poco más para que carguen elementos dinámicos
                await asyncio.sleep(2)
                
                receta = await self._extraer_receta(page, url)
                return receta
            finally:
                await browser.close()
    
    @abstractmethod
    async def _extraer_receta(self, page, url: str) -> RecetaScraped:
        """
        Método abstracto que debe implementar cada scraper específico.
        
        Args:
            page: Página de Playwright con el contenido cargado.
            url: URL original de la receta.
            
        Returns:
            RecetaScraped con los datos extraídos.
        """
        pass
    
    async def _extraer_texto_seguro(self, page, selector: str, default: str = "") -> str:
        """
        Extrae texto de un selector de forma segura.
        
        Args:
            page: Página de Playwright.
            selector: Selector CSS del elemento.
            default: Valor por defecto si no se encuentra.
            
        Returns:
            Texto extraído o valor por defecto.
        """
        try:
            elemento = await page.query_selector(selector)
            if elemento:
                return (await elemento.inner_text()).strip()
        except Exception:
            pass
        return default
    
    async def _extraer_atributo_seguro(self, page, selector: str, atributo: str, default: str = "") -> str:
        """
        Extrae un atributo de un elemento de forma segura.
        
        Args:
            page: Página de Playwright.
            selector: Selector CSS del elemento.
            atributo: Nombre del atributo a extraer.
            default: Valor por defecto si no se encuentra.
            
        Returns:
            Valor del atributo o valor por defecto.
        """
        try:
            elemento = await page.query_selector(selector)
            if elemento:
                valor = await elemento.get_attribute(atributo)
                return valor.strip() if valor else default
        except Exception:
            pass
        return default
    
    async def _extraer_lista_textos(self, page, selector: str) -> List[str]:
        """
        Extrae una lista de textos de múltiples elementos.
        
        Args:
            page: Página de Playwright.
            selector: Selector CSS de los elementos.
            
        Returns:
            Lista de textos extraídos.
        """
        try:
            elementos = await page.query_selector_all(selector)
            textos = []
            for elemento in elementos:
                texto = (await elemento.inner_text()).strip()
                if texto:
                    textos.append(texto)
            return textos
        except Exception:
            return []
    
    async def _esperar_cualquier_selector(
        self, 
        page, 
        selectores: List[str], 
        timeout: int = 10000
    ) -> Optional[str]:
        """
        Espera a que cualquiera de los selectores exista en la página.
        Retorna el selector que encontró primero.
        
        Args:
            page: Página de Playwright.
            selectores: Lista de selectores CSS a probar.
            timeout: Tiempo máximo de espera en ms.
            
        Returns:
            El selector que se encontró, o None si ninguno existe.
        """
        tiempo_por_selector = max(timeout // len(selectores), 1000)
        
        for selector in selectores:
            try:
                await page.wait_for_selector(selector, timeout=tiempo_por_selector)
                self._log(f"Selector encontrado: {selector}")
                return selector
            except Exception:
                continue
        
        self._log(f"Ningún selector encontrado de: {selectores}")
        return None
    
    async def _hacer_scroll_para_lazy_loading(
        self, 
        page, 
        scrolls: int = 5, 
        delay_ms: int = 500
    ):
        """
        Hace scroll gradual para activar lazy loading.
        
        Args:
            page: Página de Playwright.
            scrolls: Cantidad de scrolls a hacer.
            delay_ms: Delay entre scrolls en milisegundos.
        """
        for _ in range(scrolls):
            await page.evaluate('window.scrollBy(0, 300)')
            await page.wait_for_timeout(delay_ms)
        
        # Volver arriba
        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(500)
    
    async def _esperar_contenido_cargado(self, page, timeout: int = 30000):
        """
        Espera a que el contenido principal esté cargado.
        Usa múltiples estrategias.
        
        Args:
            page: Página de Playwright.
            timeout: Tiempo máximo de espera en ms.
        """
        try:
            # Estrategia 1: Esperar networkidle
            await page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception:
            pass
        
        try:
            # Estrategia 2: Esperar que no haya spinners/loaders
            await page.wait_for_function('''
                () => {
                    const loaders = document.querySelectorAll('.loading, .spinner, [class*="loader"]');
                    return loaders.length === 0 || 
                           Array.from(loaders).every(el => el.offsetParent === null);
                }
            ''', timeout=10000)
        except Exception:
            pass
    
    def _log(self, mensaje: str):
        """
        Log de debug para el scraper.
        
        Args:
            mensaje: Mensaje a loguear.
        """
        print(f"[{self.__class__.__name__}] {mensaje}")
    
    async def buscar_recetas(
        self,
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None,
        limite: int = 50
    ) -> List[dict]:
        """
        Busca recetas en el sitio según los criterios dados.
        
        Este método navega a la página de búsqueda del sitio y extrae
        una lista de URLs de recetas que coinciden con los criterios.
        
        Args:
            palabra_clave: Texto a buscar (opcional, si es None busca recetas populares).
            filtros: Diccionario con filtros dietéticos:
                     {"sin_tacc": bool, "vegetariana": bool, "vegana": bool}
            limite: Cantidad máxima de recetas a retornar.
            
        Returns:
            Lista de diccionarios con datos básicos de cada receta encontrada:
            [{"url": str, "titulo": str, "imagen_preview": str}, ...]
        """
        from playwright.async_api import async_playwright
        
        await self._esperar_rate_limit()
        
        async with async_playwright() as playwright:
            browser, page = await self._crear_contexto_playwright(playwright)
            
            try:
                # Construir y navegar a la URL de búsqueda
                url_busqueda = self._construir_url_busqueda(palabra_clave, filtros)
                await page.goto(url_busqueda, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                # Extraer la lista de recetas encontradas
                recetas = await self._extraer_lista_recetas(page, limite)
                return recetas
            except Exception as e:
                # Retornar lista vacía si hay error (el servicio manejará los errores)
                return []
            finally:
                await browser.close()
    
    def _construir_url_busqueda(
        self, 
        palabra_clave: Optional[str] = None,
        filtros: Optional[dict] = None
    ) -> str:
        """
        Construye la URL de búsqueda para el sitio.
        
        Cada scraper debe sobrescribir este método para generar
        la URL de búsqueda específica del sitio.
        
        Args:
            palabra_clave: Texto a buscar.
            filtros: Filtros dietéticos a aplicar.
            
        Returns:
            URL de búsqueda del sitio.
        """
        # Implementación por defecto - cada scraper puede sobrescribir
        dominio = self.dominios_soportados[0] if self.dominios_soportados else ""
        if palabra_clave:
            return f"https://{dominio}/search?q={palabra_clave}"
        return f"https://{dominio}/"
    
    async def _extraer_lista_recetas(self, page, limite: int) -> List[dict]:
        """
        Extrae la lista de recetas de una página de resultados.
        
        Cada scraper debe sobrescribir este método para extraer
        los datos específicos de su sitio.
        
        Args:
            page: Página de Playwright con resultados de búsqueda.
            limite: Cantidad máxima de recetas a extraer.
            
        Returns:
            Lista de diccionarios con URL, título e imagen de cada receta.
        """
        # Implementación por defecto - cada scraper debe sobrescribir
        return []
