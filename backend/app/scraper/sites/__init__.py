"""
Scrapers específicos para cada sitio de recetas.
"""

from app.scraper.sites.cookpad import CookpadScraper
from app.scraper.sites.directo_al_paladar import DirectoAlPaladarScraper
from app.scraper.sites.rechupete import RechupeteScraper
from app.scraper.sites.allrecipes import AllRecipesScraper
from app.scraper.sites.tasty import TastyScraper
from app.scraper.sites.paulina_cocina import PaulinaCocinaScraper
from app.scraper.sites.soy_celiaco import SoyCeliacoScraper
from app.scraper.sites.hellofresh import HelloFreshScraper
from app.scraper.sites.cocineros_argentinos import CocinerosArgentinosScraper
from app.scraper.sites.recetas_essen import RecetasEssenScraper

__all__ = [
    "CookpadScraper",
    "DirectoAlPaladarScraper",
    "RechupeteScraper",
    "AllRecipesScraper",
    "TastyScraper",
    "PaulinaCocinaScraper",
    "SoyCeliacoScraper",
    "HelloFreshScraper",
    "CocinerosArgentinosScraper",
    "RecetasEssenScraper"
]
