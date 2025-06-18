"""
projekt.backend.ai

Enthält AI-Utilities für Anschreiben-Generierung,
Job-Matching-Bewertung und Job-Beschreibung-Formatierung
via Google Gemini API.
"""

__version__ = "0.1.0"

__all__ = ["GeminiClient", "TextProcessor"]

from .gemini_client import GeminiClient
from .text_processor import TextProcessor