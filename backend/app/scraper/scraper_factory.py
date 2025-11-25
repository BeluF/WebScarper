"""
Factory para crear el scraper adecuado según la URL.

Detecta automáticamente qué scraper usar basándose en el dominio de la URL.
"""

from typing import Optional, Type, List
from urllib.parse import urlparse

from app.scraper.base_scraper import BaseScraper
from app.scraper.proxy_manager import ProxyManager


class ScraperFactory:
    """
    Factory que crea el scraper apropiado para una URL dada.
    
    Mantiene un registro de todos los scrapers disponibles y
    selecciona automáticamente el correcto basándose en el dominio.
    """
    
    # Lista de clases de scrapers registrados
    _scrapers: List[Type[BaseScraper]] = []
    _proxy_manager: Optional[ProxyManager] = None
    
    @classmethod
    def registrar_scraper(cls, scraper_class: Type[BaseScraper]):
        """
        Registra una clase de scraper en la factory.
        
        Args:
            scraper_class: Clase del scraper a registrar.
        """
        if scraper_class not in cls._scrapers:
            cls._scrapers.append(scraper_class)
    
    @classmethod
    def establecer_proxy_manager(cls, proxy_manager: ProxyManager):
        """
        Establece el gestor de proxies para los scrapers.
        
        Args:
            proxy_manager: Instancia del gestor de proxies.
        """
        cls._proxy_manager = proxy_manager
    
    @classmethod
    def obtener_scraper(cls, url: str) -> Optional[BaseScraper]:
        """
        Obtiene el scraper adecuado para la URL dada.
        
        Args:
            url: URL de la receta a scrapear.
            
        Returns:
            Instancia del scraper adecuado o None si no hay soporte.
        """
        # Cargar los scrapers si aún no se han cargado
        cls._cargar_scrapers()
        
        for scraper_class in cls._scrapers:
            if scraper_class.soporta_url(url):
                proxy = None
                if cls._proxy_manager:
                    proxy = cls._proxy_manager.obtener_proxy()
                return scraper_class(proxy=proxy)
        
        return None
    
    @classmethod
    def obtener_sitios_soportados(cls) -> List[dict]:
        """
        Obtiene la lista de sitios soportados.
        
        Returns:
            Lista de diccionarios con información de cada sitio.
        """
        cls._cargar_scrapers()
        
        sitios = []
        for scraper_class in cls._scrapers:
            sitios.append({
                "nombre": scraper_class.nombre_sitio,
                "dominios": scraper_class.dominios_soportados
            })
        return sitios
    
    @classmethod
    def url_soportada(cls, url: str) -> bool:
        """
        Verifica si una URL está soportada por algún scraper.
        
        Args:
            url: URL a verificar.
            
        Returns:
            True si la URL está soportada.
        """
        cls._cargar_scrapers()
        
        return any(
            scraper_class.soporta_url(url) 
            for scraper_class in cls._scrapers
        )
    
    @classmethod
    def _cargar_scrapers(cls):
        """Carga todos los scrapers disponibles."""
        if cls._scrapers:
            return
        
        # Importar todos los scrapers del módulo sites
        from app.scraper.sites import (
            CookpadScraper,
            DirectoAlPaladarScraper,
            RechupeteScraper,
            AllRecipesScraper,
            TastyScraper,
            PaulinaCocinaScraper,
            SoyCeliacoScraper,
            HelloFreshScraper,
            CocinerosArgentinosScraper,
            RecetasEssenScraper
        )
        
        # Registrar todos los scrapers
        cls._scrapers = [
            CookpadScraper,
            DirectoAlPaladarScraper,
            RechupeteScraper,
            AllRecipesScraper,
            TastyScraper,
            PaulinaCocinaScraper,
            SoyCeliacoScraper,
            HelloFreshScraper,
            CocinerosArgentinosScraper,
            RecetasEssenScraper
        ]
