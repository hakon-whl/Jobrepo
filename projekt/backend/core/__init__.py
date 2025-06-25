# projekt/backend/core/__init__.py

from .models import (
    JobSource,
    AIModel,
    SearchCriteria,
    ApplicantProfile,
    JobDetails,
    JobMatchResult,
    ScrapingSession,
    PDFGenerationConfig
)

from .config import (
    PathConfig,
    AIConfig,
    ScrapingConfig,
    AppConfig,
    SITE_CONFIGS,
    app_config
)

__all__ = [
    # Models
    'JobSource',
    'AIModel',
    'SearchCriteria',
    'ApplicantProfile',
    'JobDetails',
    'JobMatchResult',
    'ScrapingSession',
    'PDFGenerationConfig',

    # Config
    'PathConfig',
    'AIConfig',
    'ScrapingConfig',
    'AppConfig',
    'SITE_CONFIGS',
    'app_config'
]