import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

class JobSource(Enum):
    STEPSTONE       = "StepStone"
    XING            = "Xing"
    STELLENANZEIGEN = "Stellenanzeigen"

class AIModel(Enum):
    GEMENI_PRO = "gemini-2.5-pro-preview-05-06"
    GEMENI_FLASH = "gemini-2.5-flash-preview-05-20"
    GEMINI_FLASH_CHEAP = "gemini-2.5-flash-lite-preview-06-17"

@dataclass
class PathConfig:
    frontend_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend")
    temp_pdfs_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\temp_pdfs")
    prompts_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\ai\prompts")
    logs_dir: Path = Path(r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\logs")

    @property
    def build_dir(self) -> Path:
        return self.frontend_dir / "build"


@dataclass
class AIConfig:
    gemini_api_key: str = field(default_factory=lambda: os.getenv('AIzaSyB880bqvOVEs-uBpdukKPIaRYGMfvSUvdo'))

    cover_letter_model_premium: AIModel = AIModel.GEMENI_PRO
    cover_letter_temperature_premium: float = 0.5
    cover_letter_min_rating_premium: float = 8

    cover_letter_model: AIModel = AIModel.GEMENI_FLASH
    cover_letter_temperature: float = 0.5
    cover_letter_min_rating: float = 5

    formatting_model: AIModel = AIModel.GEMENI_FLASH
    formatting_temperature: float = 0.2

    rating_model: AIModel = AIModel.GEMINI_FLASH_CHEAP
    rating_temperature: float = 0.01


@dataclass
class ScrapingConfig:
    max_total_jobs_per_session: int = 200
    max_jobs_to_prozess_session: int = 20

    page_request_delay_min: float = 0.3
    page_request_delay_max: float = 0.8
    item_request_delay_min: float = 0.2
    item_request_delay_max: float = 0.5

    max_retries: int = 2
    retry_delay_base: float = 1.5
    retry_delay_max: float = 10.0
    retry_on_status_codes: List[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )

    request_timeout: int = 15
    page_load_timeout: int = 12
    implicit_wait: int = 3
    explicit_wait: int = 8

    user_agent_rotation_chance: float = 0.15

    selenium_emulate_mobile_default: bool   = False
    selenium_wait_time_default: int        = 1
    selenium_scroll_iterations_default: int= 10
    selenium_scroll_wait_time_default: float = 0.5
    selenium_window_width_default: int     = 400
    selenium_window_height_default: int    = 900


SITE_CONFIGS: Dict[JobSource, Dict[str, Any]] = {
    JobSource.STEPSTONE: {
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

    JobSource.XING: {
        "base_url": "https://www.xing.com",
        "search_url_template": "/jobs/search?keywords={jobTitle}&location={location}&radius={radius}",
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
        "job_url": {
            "selector": "``script_regex``",
            "attribute": "script",
            "regex_pattern": r'"link":"https://www.stellenanzeigen.de(/job/[^"]+)"'
        },
        "job_content_selector": "script[type='application/ld+json']",
    }
}

@dataclass
class AppConfig:
    paths: PathConfig = field(default_factory=PathConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    site_configs: Dict[JobSource, Dict[str, Any]] = field(default_factory=lambda: SITE_CONFIGS)
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")

app_config = AppConfig()