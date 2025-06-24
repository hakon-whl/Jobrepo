from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class JobSource(Enum):
    STEPSTONE = "StepStone"
    XING = "Xing"
    STELLENANZEIGEN = "Stellenanzeigen"


class AIModel(Enum):
    PRO = "gemini-2.5-pro-preview-05-06"
    FLASH = "gemini-2.5-flash-preview-05-20"
    FLASH_2 = "gemini-2.5-flash-lite-preview-06-17"


@dataclass
class PathConfig:
    """Konfiguration für Dateipfade"""
    frontend_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
    temp_pdfs_dir: str = r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\temp_pdfs"
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
    # === API-Konfiguration ===
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv('GEMINI_API_KEY', 'AIzaSyB880bqvOVEs-uBpdukKPIaRYGMfvSUvdo'))

    # === ANSCHREIBEN-GENERIERUNG ===
    cover_letter_model: AIModel = AIModel.FLASH
    cover_letter_temperature: float = 0.5
    cover_letter_min_rating: float = 5
    cover_letter_max_tokens: Optional[int] = None

    # === JOB-RATING ===
    rating_model: AIModel = AIModel.FLASH_2
    rating_temperature: float = 0.05
    rating_max_tokens: Optional[int] = 10

    # === JOB-BESCHREIBUNG FORMATIERUNG ===
    formatting_model: AIModel = AIModel.FLASH_2
    formatting_temperature: float = 0.2
    formatting_max_tokens: Optional[int] = None

    # === ALLGEMEINE LLM-EINSTELLUNGEN ===
    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 0

    # === PREMIUM-SCHWELLENWERTE ===
    premium_rating_threshold: int = 8
    auto_upgrade_to_premium: bool = False

    # === LEGACY (für Rückwärtskompatibilität) ===
    @property
    def default_model(self) -> AIModel:
        """Legacy-Property für bestehenden Code"""
        return self.cover_letter_model

    @property
    def default_temperature(self) -> float:
        """Legacy-Property für bestehenden Code"""
        return self.cover_letter_temperature


@dataclass
class ScrapingConfig:
    """Optimierte Scraping-Konfiguration"""
    # === ALLGEMEINE LIMITS ===
    max_pages_per_site: int = 10
    max_jobs_per_session: int = 50
    max_total_jobs_per_site: int = 200
    jobs_per_page_limit: int = 50

    # === REQUEST-TIMING (optimiert) ===
    page_request_delay_min: float = 0.3
    page_request_delay_max: float = 0.8
    item_request_delay_min: float = 0.2
    item_request_delay_max: float = 0.5

    # === RETRY-STRATEGIE ===
    max_retries: int = 2
    retry_delay_base: float = 1.5
    retry_delay_max: float = 10.0
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

    # === TIMEOUTS (optimiert) ===
    request_timeout: int = 15
    page_load_timeout: int = 12
    implicit_wait: int = 3
    explicit_wait: int = 8

    # === ANTI-BOT-MAßNAHMEN ===
    user_agent_rotation_chance: float = 0.15

    # === SELENIUM-KONFIGURATION (optimiert) ===
    selenium_emulate_mobile_default: bool = False
    selenium_wait_time_default: int = 1
    selenium_scroll_iterations_default: int = 10
    selenium_scroll_wait_time_default: int = 0.5
    selenium_window_width_default: int = 400
    selenium_window_height_default: int = 900
@dataclass
class LoggingConfig:
    """Konfiguration für Logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_logging: bool = True
    file_logging: bool = True
    max_file_size: int = 10 * 1024 * 1024
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


# User Agents für Scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.2420.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

# Site-Konfigurationen - jetzt mit JobSource statt Site
SITE_CONFIGS = {
    JobSource.STEPSTONE: {
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
    JobSource.XING: {
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
    JobSource.STELLENANZEIGEN: {
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
            "selector": "``script_regex``",
            "attribute": "script",
            "regex_pattern": r'"link":"https://www.stellenanzeigen.de(/job/[^"]+)"'
        },
        "job_content_selector": "script[type='application/ld+json']",
    }
}


def get_site_config_by_string(site_name_str: str) -> dict | None:
    """Gibt Konfiguration für Site-Name als String zurück"""
    try:
        # Versuche zuerst direkten Enum-Match
        for job_source in JobSource:
            if job_source.value == site_name_str:
                return SITE_CONFIGS.get(job_source)

        # Fallback für verschiedene Schreibweisen
        site_map = {
            "StepStone": JobSource.STEPSTONE,
            "Xing": JobSource.XING,
            "Stellenanzeigen": JobSource.STELLENANZEIGEN,
            "Stellenanzeigen.de": JobSource.STELLENANZEIGEN
        }

        job_source = site_map.get(site_name_str)
        return SITE_CONFIGS.get(job_source) if job_source else None

    except Exception as e:
        logger.warning(f"Fehler beim Abrufen der Site-Konfiguration für '{site_name_str}': {e}")
        return None


def setup_logging(logging_config, logs_dir):
    """Minimal logging setup"""

    # Nur kritische Config-Logs
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    # Basis Logging-Konfiguration ohne Ausgaben
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )

    # Werkzeug und andere Libraries stumm schalten
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

# Globale App-Konfiguration
app_config = AppConfig()