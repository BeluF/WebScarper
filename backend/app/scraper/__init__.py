"""
Módulo de scraping para el sistema de recetario.
"""

from app.scraper.base_scraper import BaseScraper
from app.scraper.scraper_factory import ScraperFactory
from app.scraper.proxy_manager import ProxyManager

__all__ = ["BaseScraper", "ScraperFactory", "ProxyManager"]
