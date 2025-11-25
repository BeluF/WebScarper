"""
Clase base abstracta para scrapers de recetas.

Define la interfaz común que deben implementar todos los scrapers específicos.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
import asyncio
import time

from app.config import SCRAPER_TIMEOUT, SCRAPER_HEADLESS, RATE_LIMIT_DELAY


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
