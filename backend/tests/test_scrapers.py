"""
Tests para los scrapers del sistema de recetario.
"""

import pytest
from app.scraper.scraper_factory import ScraperFactory
from app.scraper.proxy_manager import ProxyManager


class TestScraperFactory:
    """Tests para la factory de scrapers."""
    
    def test_url_cookpad_soportada(self):
        """Verifica que las URLs de Cookpad sean reconocidas."""
        assert ScraperFactory.url_soportada("https://cookpad.com/ar/recetas/123")
        assert ScraperFactory.url_soportada("https://www.cookpad.com/es/recetas/456")
    
    def test_url_allrecipes_soportada(self):
        """Verifica que las URLs de AllRecipes sean reconocidas."""
        assert ScraperFactory.url_soportada("https://www.allrecipes.com/recipe/123")
    
    def test_url_tasty_soportada(self):
        """Verifica que las URLs de Tasty sean reconocidas."""
        assert ScraperFactory.url_soportada("https://tasty.co/recipe/test-recipe")
    
    def test_url_no_soportada(self):
        """Verifica que las URLs no soportadas sean rechazadas."""
        assert not ScraperFactory.url_soportada("https://unsupported-site.com/recipe")
        assert not ScraperFactory.url_soportada("https://google.com")
    
    def test_obtener_scraper_para_cookpad(self):
        """Verifica que se obtenga el scraper correcto para Cookpad."""
        scraper = ScraperFactory.obtener_scraper("https://cookpad.com/ar/recetas/123")
        assert scraper is not None
        assert scraper.nombre_sitio == "Cookpad"
    
    def test_obtener_scraper_para_url_invalida(self):
        """Verifica que se retorne None para URLs no soportadas."""
        scraper = ScraperFactory.obtener_scraper("https://unsupported.com/recipe")
        assert scraper is None
    
    def test_obtener_sitios_soportados(self):
        """Verifica la lista de sitios soportados."""
        sitios = ScraperFactory.obtener_sitios_soportados()
        assert len(sitios) == 10
        nombres = [s["nombre"] for s in sitios]
        assert "Cookpad" in nombres
        assert "AllRecipes" in nombres
        assert "Tasty" in nombres


class TestProxyManager:
    """Tests para el gestor de proxies."""
    
    def test_sin_proxies_habilitados(self):
        """Verifica comportamiento sin proxies."""
        manager = ProxyManager(enabled=False)
        assert manager.obtener_proxy() is None
    
    def test_agregar_proxy(self):
        """Verifica agregar proxies manualmente."""
        manager = ProxyManager(enabled=True)
        manager.agregar_proxy("http://proxy1:8080")
        manager.agregar_proxy("http://proxy2:8080")
        assert manager.cantidad_proxies == 2
    
    def test_rotacion_proxies(self):
        """Verifica la rotación round-robin de proxies."""
        manager = ProxyManager(enabled=True)
        manager.agregar_proxy("http://proxy1:8080")
        manager.agregar_proxy("http://proxy2:8080")
        
        proxy1 = manager.obtener_proxy()
        proxy2 = manager.obtener_proxy()
        proxy3 = manager.obtener_proxy()
        
        assert proxy1 == "http://proxy1:8080"
        assert proxy2 == "http://proxy2:8080"
        assert proxy3 == "http://proxy1:8080"  # Vuelve al primero
    
    def test_marcar_proxy_fallido(self):
        """Verifica que los proxies fallidos se excluyan."""
        manager = ProxyManager(enabled=True)
        manager.agregar_proxy("http://proxy1:8080")
        manager.agregar_proxy("http://proxy2:8080")
        
        manager.marcar_fallido("http://proxy1:8080")
        assert manager.cantidad_disponibles == 1
        
        proxy = manager.obtener_proxy()
        assert proxy == "http://proxy2:8080"
    
    def test_resetear_proxies_fallidos(self):
        """Verifica que se puedan resetear los proxies fallidos."""
        manager = ProxyManager(enabled=True)
        manager.agregar_proxy("http://proxy1:8080")
        manager.marcar_fallido("http://proxy1:8080")
        
        assert manager.cantidad_disponibles == 0
        
        manager.resetear_fallidos()
        assert manager.cantidad_disponibles == 1
