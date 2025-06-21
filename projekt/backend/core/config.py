from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# Bestehende Enums bleiben unverändert
class Site(Enum):
    STEPSTONE = "StepStone"
    XING = "Xing"
    STELLENANZEIGEN = "Stellenanzeigen"


class JobSource(Enum):
    STEPSTONE = "StepStone"
    XING = "Xing"
    STELLENANZEIGEN = "Stellenanzeigen"


class AIModel(Enum):
    FLASH = 'gemini-2.5-flash-preview-05-20'
    PRO = 'gemini-2.5-pro-preview-05-06'
    FLASH_2 = 'gemini-2.0-flash'


@dataclass
class PathConfig:
    """Konfiguration für Dateipfade"""
    frontend_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
    temp_pdfs_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\temp_pdfs"
    prompts_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\ai\prompts"
    logs_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\logs"

    @property
    def build_dir(self) -> str:
        return os.path.join(self.frontend_dir, "build")

    def ensure_directories(self) -> None:
        """Erstellt alle notwendigen Verzeichnisse"""
        for dir_path in [self.temp_pdfs_dir, self.logs_dir]:
            os.makedirs(dir_path, exist_ok=True)


@dataclass
class AIConfig:
    """Konfiguration für AI-Services"""
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv('GEMINI_API_KEY', 'AIzaSyBI4KCnGbDQi9GGi3MB35lQJ-TSNTQH6oI'))
    default_model: AIModel = AIModel.FLASH
    default_temperature: float = 0.5
    rating_temperature: float = 0.05
    premium_rating_threshold: int = 8


@dataclass
class ScrapingConfig:
    """Konfiguration für Web-Scraping"""
    max_pages_per_site: int = 6
    max_jobs_per_session: int = 20
    default_request_delay: tuple = (2.0, 5.0)
    max_retries: int = 3
    retry_delay: int = 10
    timeout: int = 10

    selenium_emulate_mobile_default: bool = True
    selenium_wait_time_default: int = 10
    selenium_scroll_iterations_default: int = 10
    selenium_scroll_wait_time_default: int = 2



@dataclass
class LoggingConfig:
    """Konfiguration für Logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_logging: bool = True
    file_logging: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class AppConfig:
    """Zentrale Anwendungskonfiguration"""
    paths: PathConfig = field(default_factory=PathConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'True').lower() == 'true')

    def __post_init__(self):
        """Post-Initialisierung der Konfiguration"""
        self.paths.ensure_directories()


# User Agents für Scraping (bleibt unverändert)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.2420.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

# Site-Konfigurationen (bleiben unverändert)
SITE_CONFIGS = {
    Site.STEPSTONE: {
        "base_url": "https://www.stepstone.de",
        "search_url_template": "/jobs/{jobTitle}/in-{location}?radius={radius}&di={discipline}&page={seite}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.5",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        },
        "job_url": {
            "selector": 'a[href^="/stellenangebote"]',
            "attribute": "href"
        },
        "max_page_selector": 'span[class="res-httn92"]',
        "job_content_selector": 'div[data-at="job-ad-content"]',
        "job_pages_selector": 'span[class="res-tqs0ve"]',
        "job_titel_selector": 'strong[data-at="header-job-title"]',
    },
    Site.XING: {
        "base_url": "https://www.xing.com",
        "search_url_template": "/jobs/search?keywords={jobTitle}&location={location}&radius={radius}",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "de-DE,de;q=0.9,en-DE;q=0.8,en;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        },
        "job_url": {
            "selector": 'article[data-testid="job-search-result"] a',
            "attribute": "href"
        },
        "job_content_selector": "div[data-testid='expandable-content']",
        "job_titel_selector": "h2[data-xds='Headline']",
    },
    Site.STELLENANZEIGEN: {
        "base_url": "https://www.stellenanzeigen.de/",
        "search_url_template": "/suche/?fulltext={jobTitle}&locationIds={location}&perimeterRadius={radius}",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "de-DE,de;q=0.9,en-DE;q=0.8,en;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        },
        "job_url": {
            "selector": "script_regex",
            "attribute": "script",
            "regex_pattern": r'"link":"https://www.stellenanzeigen.de(/job/[^"]+)"'
        },
        "job_content_selector": "script[type='application/ld+json']",
    }
}


def get_site_config(site_name_enum: Site) -> dict | None:
    return SITE_CONFIGS.get(site_name_enum)


def get_site_config_by_string(site_name_str: str) -> dict | None:
    try:
        site_enum_member = Site[site_name_str.upper().replace(" ", "_").replace(".", "_")]
        return SITE_CONFIGS.get(site_enum_member)
    except KeyError:
        for site_enum, config in SITE_CONFIGS.items():
            if site_enum.value == site_name_str:
                return config
        logger.warning(f"Keine Konfiguration für Seite '{site_name_str}' gefunden.")
        return None


def setup_logging(config: LoggingConfig, logs_dir: str) -> None:
    """Konfiguriert das Logging-System"""
    import logging.handlers

    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))

    # Alle bestehenden Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Formatter definieren
    formatter = logging.Formatter(config.format)

    # Console Handler
    if config.console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File Handler
    if config.file_logging:
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, 'app.log')

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Erste Nachricht loggen
    logger.info("Logging-System initialisiert")
    logger.info(f"Log-Level: {config.level}")
    logger.info(f"Console-Logging: {config.console_logging}")
    logger.info(f"File-Logging: {config.file_logging}")


# Globale App-Konfiguration
app_config = AppConfig()