"""
projekt.backend.utils

Hilfsfunktionen für HTML-Parsing und PDF-Erstellung.
"""

__version__ = "0.1.0"

__all__ = [
    "extract_text_from_selector",
    "extract_attribute_from_selector",
    "PdfUtils",
]

from .html_parser import extract_text_from_selector, extract_attribute_from_selector
from .pdf_utils import PdfUtils