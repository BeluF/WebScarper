"""
Tests para los scrapers del sistema de recetario.
"""

import pytest
from app.scraper.scraper_factory import ScraperFactory
from app.scraper.proxy_manager import ProxyManager
from app.scraper.base_scraper import (
    validar_receta,
    detectar_idioma,
    separar_ingredientes_y_pasos,
    RecetaScraped
)


class TestValidacionRecetas:
    """Tests para la validación de recetas."""
    
    def test_receta_valida(self):
        """Verifica que una receta completa sea válida."""
        receta = {
            'titulo': 'Empanadas de carne',
            'ingredientes': ['500g de carne molida', '2 cebollas', 'Comino'],
            'pasos': ['Picar las cebollas', 'Cocinar la carne', 'Armar las empanadas']
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is True
        assert mensaje == ""
    
    def test_receta_sin_titulo(self):
        """Verifica que una receta sin título sea inválida."""
        receta = {
            'titulo': '',
            'ingredientes': ['500g de carne'],
            'pasos': ['Cocinar la carne']
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is False
        assert 'título' in mensaje.lower()
    
    def test_receta_sin_titulo_default(self):
        """Verifica que una receta con título 'Sin título' sea inválida."""
        receta = {
            'titulo': 'Sin título',
            'ingredientes': ['500g de carne'],
            'pasos': ['Cocinar la carne']
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is False
        assert 'título' in mensaje.lower()
    
    def test_receta_sin_ingredientes(self):
        """Verifica que una receta sin ingredientes sea inválida."""
        receta = {
            'titulo': 'Receta de prueba',
            'ingredientes': [],
            'pasos': ['Paso 1', 'Paso 2']
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is False
        assert 'ingredientes' in mensaje.lower()
    
    def test_receta_sin_pasos(self):
        """Verifica que una receta sin pasos sea inválida."""
        receta = {
            'titulo': 'Receta de prueba',
            'ingredientes': ['Ingrediente 1'],
            'pasos': []
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is False
        assert 'pasos' in mensaje.lower()
    
    def test_receta_con_ingredientes_vacios(self):
        """Verifica que una receta con ingredientes vacíos sea inválida."""
        receta = {
            'titulo': 'Receta de prueba',
            'ingredientes': ['', '  ', ''],
            'pasos': ['Paso 1']
        }
        es_valida, mensaje = validar_receta(receta)
        assert es_valida is False
        assert 'ingredientes' in mensaje.lower()


class TestDeteccionIdioma:
    """Tests para la detección de idioma."""
    
    def test_detectar_espanol(self):
        """Verifica detección de texto en español."""
        texto = "Mezclar los ingredientes en una olla. Cocinar durante 20 minutos. Añadir sal al gusto."
        idioma = detectar_idioma(texto)
        assert idioma == 'es'
    
    def test_detectar_ingles(self):
        """Verifica detección de texto en inglés."""
        texto = "Mix the ingredients in a pot. Cook for 20 minutes. Add salt to taste."
        idioma = detectar_idioma(texto)
        assert idioma == 'en'
    
    def test_detectar_desconocido(self):
        """Verifica detección de texto sin palabras clave."""
        texto = "Lorem ipsum dolor sit amet"
        idioma = detectar_idioma(texto)
        assert idioma == 'desconocido'
    
    def test_detectar_espanol_receta_completa(self):
        """Verifica detección en una receta completa en español."""
        texto = """
        Empanadas de carne
        Ingredientes: 500g de carne molida, 2 cucharadas de comino
        Preparación: Picar las cebollas y cocinar a fuego medio.
        Tiempo de cocción: 30 minutos. Porciones: 12 empanadas.
        """
        idioma = detectar_idioma(texto)
        assert idioma == 'es'


class TestSepararIngredientesYPasos:
    """Tests para la separación de ingredientes y pasos."""
    
    def test_separar_lista_mixta(self):
        """Verifica separación de una lista mezclada."""
        items = [
            '500g de carne molida',
            '2 cucharadas de aceite',
            'Picar las cebollas finamente y reservar',
            '1 taza de harina',
            'Cocinar a fuego medio durante 20 minutos'
        ]
        ingredientes, pasos = separar_ingredientes_y_pasos(items)
        
        # Los items con cantidades deben ir a ingredientes
        assert '500g de carne molida' in ingredientes
        assert '2 cucharadas de aceite' in ingredientes
        assert '1 taza de harina' in ingredientes
        
        # Los items largos con verbos de cocina deben ir a pasos
        assert 'Picar las cebollas finamente y reservar' in pasos
        assert 'Cocinar a fuego medio durante 20 minutos' in pasos
    
    def test_separar_lista_solo_ingredientes(self):
        """Verifica separación cuando solo hay ingredientes."""
        items = [
            '500g de carne',
            '100ml de leche',
            '2 huevos',
            'Sal'
        ]
        ingredientes, pasos = separar_ingredientes_y_pasos(items)
        assert len(ingredientes) == 4
        assert len(pasos) == 0
    
    def test_separar_lista_vacia(self):
        """Verifica separación de lista vacía."""
        ingredientes, pasos = separar_ingredientes_y_pasos([])
        assert ingredientes == []
        assert pasos == []
    
    def test_ignorar_items_vacios(self):
        """Verifica que se ignoren items vacíos."""
        items = ['500g de carne', '', '  ', 'Sal']
        ingredientes, pasos = separar_ingredientes_y_pasos(items)
        assert len(ingredientes) == 2


class TestRecetaScrapedValidacion:
    """Tests para la validación en la clase RecetaScraped."""
    
    def test_receta_scraped_validar(self):
        """Verifica método validar de RecetaScraped."""
        receta = RecetaScraped(
            titulo='Empanadas de carne',
            url_origen='https://test.com/receta',
            sitio_origen='Test',
            ingredientes=['500g de carne', 'Cebollas'],
            pasos=['Picar', 'Cocinar']
        )
        es_valida, mensaje = receta.validar()
        assert es_valida is True
    
    def test_receta_scraped_detectar_idioma_espanol(self):
        """Verifica detección de idioma español en RecetaScraped."""
        receta = RecetaScraped(
            titulo='Empanadas de carne con verduras',
            url_origen='https://test.com/receta',
            sitio_origen='Test',
            descripcion='Una deliciosa receta de empanadas para cocinar en familia',
            ingredientes=['500g de carne molida', '2 cucharadas de aceite'],
            pasos=['Mezclar todos los ingredientes', 'Cocinar durante 30 minutos']
        )
        idioma = receta.detectar_idioma()
        assert idioma == 'es'
    
    def test_receta_scraped_detectar_idioma_ingles(self):
        """Verifica detección de idioma inglés en RecetaScraped."""
        receta = RecetaScraped(
            titulo='Beef Empanadas Recipe',
            url_origen='https://test.com/recipe',
            sitio_origen='Test',
            descripcion='A delicious recipe to cook with your family',
            ingredientes=['500g ground beef', '2 tablespoons oil'],
            pasos=['Mix all ingredients', 'Cook for 30 minutes']
        )
        idioma = receta.detectar_idioma()
        assert idioma == 'en'


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


class TestBaseScraperHelpers:
    """Tests para los métodos helper del BaseScraper para contenido dinámico."""
    
    def test_log_output(self, capsys):
        """Verifica que el método _log produce salida correcta."""
        from app.scraper.sites.cookpad import CookpadScraper
        
        scraper = CookpadScraper()
        scraper._log("Test mensaje")
        
        captured = capsys.readouterr()
        assert "[CookpadScraper]" in captured.out
        assert "Test mensaje" in captured.out
    
    def test_log_con_emojis(self, capsys):
        """Verifica que el método _log funciona con emojis."""
        from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
        
        scraper = PaulinaCocinaScraper()
        scraper._log("✅ Receta extraída")
        scraper._log("⚠️ Advertencia")
        
        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "⚠️" in captured.out
    
    def test_scrapers_tienen_metodo_esperar_cualquier_selector(self):
        """Verifica que todos los scrapers afectados tienen el método helper."""
        from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
        from app.scraper.sites.tasty import TastyScraper
        from app.scraper.sites.rechupete import RechupeteScraper
        from app.scraper.sites.cookpad import CookpadScraper
        
        scrapers = [
            PaulinaCocinaScraper(),
            TastyScraper(),
            RechupeteScraper(),
            CookpadScraper()
        ]
        
        for scraper in scrapers:
            assert hasattr(scraper, '_esperar_cualquier_selector')
            assert callable(getattr(scraper, '_esperar_cualquier_selector'))
    
    def test_scrapers_tienen_metodo_hacer_scroll(self):
        """Verifica que todos los scrapers afectados tienen el método de scroll."""
        from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
        from app.scraper.sites.tasty import TastyScraper
        from app.scraper.sites.rechupete import RechupeteScraper
        from app.scraper.sites.cookpad import CookpadScraper
        
        scrapers = [
            PaulinaCocinaScraper(),
            TastyScraper(),
            RechupeteScraper(),
            CookpadScraper()
        ]
        
        for scraper in scrapers:
            assert hasattr(scraper, '_hacer_scroll_para_lazy_loading')
            assert callable(getattr(scraper, '_hacer_scroll_para_lazy_loading'))
    
    def test_scrapers_tienen_metodo_esperar_contenido(self):
        """Verifica que todos los scrapers afectados tienen el método de espera."""
        from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
        from app.scraper.sites.tasty import TastyScraper
        from app.scraper.sites.rechupete import RechupeteScraper
        from app.scraper.sites.cookpad import CookpadScraper
        
        scrapers = [
            PaulinaCocinaScraper(),
            TastyScraper(),
            RechupeteScraper(),
            CookpadScraper()
        ]
        
        for scraper in scrapers:
            assert hasattr(scraper, '_esperar_contenido_cargado')
            assert callable(getattr(scraper, '_esperar_contenido_cargado'))
    
    def test_scraper_paulina_cocina_nombre_sitio(self):
        """Verifica configuración de PaulinaCocinaScraper."""
        from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
        
        scraper = PaulinaCocinaScraper()
        assert scraper.nombre_sitio == "Paulina Cocina"
        assert "paulinacocina.net" in scraper.dominios_soportados
    
    def test_scraper_tasty_nombre_sitio(self):
        """Verifica configuración de TastyScraper."""
        from app.scraper.sites.tasty import TastyScraper
        
        scraper = TastyScraper()
        assert scraper.nombre_sitio == "Tasty"
        assert "tasty.co" in scraper.dominios_soportados
    
    def test_scraper_rechupete_nombre_sitio(self):
        """Verifica configuración de RechupeteScraper."""
        from app.scraper.sites.rechupete import RechupeteScraper
        
        scraper = RechupeteScraper()
        assert scraper.nombre_sitio == "Recetas de Rechupete"
        assert "recetasderechupete.com" in scraper.dominios_soportados
    
    def test_scraper_cookpad_nombre_sitio(self):
        """Verifica configuración de CookpadScraper."""
        from app.scraper.sites.cookpad import CookpadScraper
        
        scraper = CookpadScraper()
        assert scraper.nombre_sitio == "Cookpad"
        assert "cookpad.com" in scraper.dominios_soportados
