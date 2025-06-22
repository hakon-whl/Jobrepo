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
    LoggingConfig,
    AppConfig,
    USER_AGENTS,
    SITE_CONFIGS,
    get_site_config_by_string,
    setup_logging,
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
    'LoggingConfig',
    'AppConfig',
    'USER_AGENTS',
    'SITE_CONFIGS',
    'get_site_config_by_string',
    'setup_logging',
    'app_config'
]