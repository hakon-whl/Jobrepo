# projekt/backend/core/__init__.py

"""
projekt.backend.core
====================

Dieses Paket enthält die zentralen Datenmodelle und die anwendungsweite
Konfiguration für die Job-Scraping- und KI-Analyse-Anwendung.
"""

# Importiere alle relevanten Klassen und Enums aus models.py
from .models import (
    JobSource,
    AIModel,
    SearchCriteria,
    ApplicantProfile,
    JobDetails,
    JobMatchResult,
    ScrapingSession,
    PDFGenerationConfig,
)

# Importiere alle relevanten Konfigurationsklassen und Hilfsfunktionen aus config.py
from .config import (
    Site, # Enum für Site-Konfigurationen
    PathConfig,
    AIConfig,
    ScrapingConfig,
    LoggingConfig,
    AppConfig,
    USER_AGENTS, # Liste der User-Agents
    SITE_CONFIGS, # Dictionary der Site-Konfigurationen
    get_site_config,
    get_site_config_by_string,
    setup_logging,
    app_config, # Die globale Anwendungsinstanz
)

__version__ = "0.1.0"
__author__ = "Hakon" # Dein Name als Autor
__description__ = "Kern-Datenmodelle und Konfiguration für die Job-Scraping- und KI-Analyse-Anwendung."

# Definiere, welche Elemente öffentlich gemacht werden, wenn jemand
# 'from projekt.backend.core import *' verwendet.
__all__ = [
    # Enums
    "JobSource",
    "AIModel",
    "Site",

    # Datenmodelle
    "SearchCriteria",
    "ApplicantProfile",
    "JobDetails",
    "JobMatchResult",
    "ScrapingSession",
    "PDFGenerationConfig",

    # Konfigurationsklassen
    "PathConfig",
    "AIConfig",
    "ScrapingConfig",
    "LoggingConfig",
    "AppConfig",

    # Konfigurationsdaten (Variablen)
    "USER_AGENTS",
    "SITE_CONFIGS",
    "app_config",

    # Hilfsfunktionen
    "get_site_config",
    "get_site_config_by_string",
    "setup_logging",
]