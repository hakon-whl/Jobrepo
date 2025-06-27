from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).parent
API_KEY_FILE = BASE_DIR / "api_key.txt"

def _load_gemini_key() -> str:
    if not API_KEY_FILE.exists():
        raise FileNotFoundError(f"API-Key Datei nicht gefunden: {API_KEY_FILE}")

    key = API_KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"API-Key Datei ist leer: {API_KEY_FILE}")

    return key

class JobSource(Enum):
    STEPSTONE = "StepStone"
    XING = "Xing"

class AIModel(Enum):
    GEMINI_PRO = "gemini-2.5-flash"
    GEMINI_FLASH = "gemini-2.5-flash-preview-04-17"
    GEMINI_FLASH_CHEAP = "gemini-2.0-flash-lite"

@dataclass
class PathConfig:
    frontend_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\frontend")
    temp_pdfs_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\temp_pdfs")
    prompts_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\ai\prompts")
    logs_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\logs")

    @property
    def build_dir(self) -> Path:
        return self.frontend_dir / "build"

@dataclass
class AIConfig:
    gemini_api_key: str = field(default_factory=_load_gemini_key)
    cover_letter_model_premium: AIModel = AIModel.GEMINI_PRO
    cover_letter_temperature_premium: float = 0.5
    cover_letter_min_rating_premium: int = 8

    cover_letter_model: AIModel = AIModel.GEMINI_FLASH
    cover_letter_temperature: float = 0.5
    cover_letter_min_rating: int = 5

    formatting_model: AIModel = AIModel.GEMINI_FLASH
    formatting_temperature: float = 0.01

    rating_model: AIModel = AIModel.GEMINI_FLASH_CHEAP
    rating_temperature: float = 0.01

@dataclass
class ScrapingConfig:
    max_jobs_to_prozess_session: int = 5

    page_request_delay_min: float = 1
    page_request_delay_max: float = 2

    max_retries: int = 3
    retry_delay_base: float = 2
    retry_delay_max: float = 10.0
    request_timeout: int = 15

    selenium_wait_time_default: int = 1
    selenium_scroll_wait_time_default: float = 0.5
    selenium_window_width_default: int = 400
    selenium_window_height_default: int = 900

SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    JobSource.STEPSTONE.value: {
        "base_url": "https://www.stepstone.de",
        "search_url_template": "/jobs/{jobTitle}/in-{location}?radius={radius}&di={discipline}&page={seite}",

        "job_url": {
            "selector": 'a[href^="/stellenangebote"]',
            "attribute": "href"
        },

        "max_page_selector": 'span[class="res-httn92"]',
        "job_content_selector": 'div[data-at="job-ad-content"]',
        "job_titel_selector": 'strong[data-at="header-job-title"]',
    },

    JobSource.XING.value: {
        "base_url": "https://www.xing.com",
        "search_url_template": "/jobs/search?keywords={jobTitle}&location={location}&radius={radius}",

        "job_url": {
            "selector": 'article[data-testid="job-search-result"] a',
            "attribute": "href"
        },

        "job_content_selector": "div[data-testid='expandable-content']",
        "job_titel_selector": "h2[data-xds='Headline']",
        "max_job_amount": "headline-styles__Headline-sc-339d833d-0 kmUSxO results-header__Headline-sc-e1bd05a1-1 iNORxT",
        "jobs_per_lazyload": 20
    },
}

@dataclass
class AppConfig:
    paths: PathConfig = field(default_factory=PathConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    site_configs: Dict[JobSource, Dict[str, Any]] = field(default_factory=lambda: SITE_CONFIGS)

app_config = AppConfig()