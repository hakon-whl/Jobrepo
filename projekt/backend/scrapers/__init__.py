"""
projekt.backend.scrapers

Enthält alle Web-Scraper für die relevanten Job-Plattformen.
"""

__version__ = "0.1.0"

__all__ = [
    "RequestBaseScraper",
    "SeleniumBaseScraper",
    "StepstoneScraper",
    "XingScraper",
    "StellenanzeigenScraper",
]

from .request_base_scraper    import RequestBaseScraper
from .selenium_base_scraper   import SeleniumBaseScraper
from .stepstone_scraper       import StepstoneScraper
from .xing_scraper            import XingScraper
from .stellenanzeigen_scraper import StellenanzeigenScraper