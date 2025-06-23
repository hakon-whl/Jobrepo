from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
import re
import os
import logging

logger = logging.getLogger(__name__)


class JobSource(Enum):
    STEPSTONE = "StepStone"
    XING = "Xing"
    STELLENANZEIGEN = "Stellenanzeigen"


class AIModel(Enum):
    FLASH = 'gemini-2.5-flash-preview-05-20'
    PRO = 'gemini-2.5-pro-preview-05-06'
    FLASH_2 = 'gemini-2.0-flash'


@dataclass
class SearchCriteria:
    job_title: str
    location: str
    radius: str
    discipline: str = ""

    def to_stepstone_params(self) -> Dict[str, Any]:
        return {
            "jobTitle": self.job_title,
            "location": self.location,
            "radius": self.radius,
            "discipline": self.discipline
        }

    def to_xing_params(self) -> Dict[str, Any]:
        return {
            "jobTitle": self.job_title,
            "location": self.location,
            "radius": self.radius
        }

    def to_stellenanzeigen_params(self) -> Dict[str, Any]:
        return {
            "jobTitle": self.job_title,
            "location": self.location,
            "radius": self.radius
        }


@dataclass
class ApplicantProfile:
    study_info: str
    interests: str
    skills: List[str]
    pdf_contents: Dict[str, str] = field(default_factory=dict)

    def to_ai_prompt_format(self) -> str:
        """Formatiert Profil für AI-Prompts"""
        skills_text = ", ".join(self.skills) if self.skills else "Keine Skills angegeben"
        profile_text = f"""
        Studium: {self.study_info}
        Interessen: {self.interests}
        Fähigkeiten: {skills_text}
        """
        logger.debug(f"Bewerber-Profil formatiert: {len(profile_text)} Zeichen")
        return profile_text

    def get_previous_cover_letters(self) -> str:
        """Kombiniert alle PDF-Inhalte zu einem String"""
        if not self.pdf_contents:
            logger.debug("Keine vorherigen Anschreiben verfügbar")
            return ""

        combined_letters = "\n\n".join(self.pdf_contents.values())
        logger.debug(
            f"Vorherige Anschreiben kombiniert: {len(combined_letters)} Zeichen aus {len(self.pdf_contents)} PDFs")
        return combined_letters


@dataclass
class JobDetails:
    title: str
    title_clean: str
    raw_text: str
    url: str
    source_site: Optional[JobSource] = None
    rating: Optional[int] = None
    formatted_description: Optional[str] = None
    cover_letter: Optional[str] = None
    is_internship: bool = field(init=False)  # Wird automatisch gesetzt

    def __post_init__(self):
        """Validierung und Bereinigung nach Initialisierung"""
        if not self.title_clean and self.title:
            self.title_clean = re.sub(r'[^a-zA-Z0-9 ]', '', self.title)

        # Automatische Prüfung auf Praktikums-Keywords
        self.is_internship = self._contains_internship_keywords()

        logger.debug(f"JobDetails erstellt: {self.title} von {self.source_site} (Praktikum: {self.is_internship})")

    def _contains_internship_keywords(self) -> bool:
        """Prüft ob Job-Title Praktikums-Keywords enthält"""
        keywords = ["Praktikant", "Praktikum", "Trainee", "Internship", "INTERN", "Intern", "Werkstudent"]
        has_keywords = any(keyword.lower() in self.title.lower() for keyword in keywords)
        return has_keywords

    @property
    def contains_internship_keywords(self) -> bool:
        """Legacy-Property für Rückwärtskompatibilität"""
        return self.is_internship

    @property
    def safe_filename(self) -> str:
        """Erstellt einen sicheren Dateinamen"""
        safe_title = self.title_clean.replace(os.sep, '_').replace('/', '_').replace('\\', '_')
        return safe_title if safe_title else 'unbekannter_titel'


@dataclass
class JobMatchResult:
    job_details: JobDetails
    rating: int
    formatted_description: str
    cover_letter: Optional[str] = None
    ai_model_used: Optional[str] = None

    def __post_init__(self):
        """Aktualisiert job_details mit rating"""
        self.job_details.rating = self.rating
        self.job_details.formatted_description = self.formatted_description
        self.job_details.cover_letter = self.cover_letter

        logger.info(f"JobMatchResult erstellt: Rating {self.rating} für '{self.job_details.title}'")

    @property
    def is_worth_processing(self) -> bool:
        """Prüft ob Job verarbeitet werden soll (Rating >= 5)"""
        from projekt.backend.core.config import app_config
        return self.rating >= app_config.ai.cover_letter_min_rating

    @property
    def needs_premium_model(self) -> bool:
        """Prüft ob Premium AI-Model benötigt wird (aus Config)"""
        from projekt.backend.core.config import app_config
        return self.rating >= app_config.ai.premium_rating_threshold

    def get_pdf_filename(self) -> str:
        """Erstellt Dateinamen für PDF"""
        return f"{self.rating}_{self.job_details.safe_filename}.pdf"


@dataclass
class ScrapingSession:
    search_criteria: SearchCriteria
    applicant_profile: ApplicantProfile
    selected_source: JobSource
    job_results: List[JobMatchResult] = field(default_factory=list)
    total_jobs_found: int = 0
    total_jobs_processed: int = 0

    def add_result(self, result: JobMatchResult):
        """Fügt ein Job-Ergebnis zur Session hinzu"""
        self.job_results.append(result)
        self.total_jobs_processed += 1
        logger.info(
            f"Job-Ergebnis hinzugefügt: Rating {result.rating} ({self.total_jobs_processed} von {self.total_jobs_found})")

    @property
    def successful_matches(self) -> List[JobMatchResult]:
        """Gibt nur die erfolgreichen Matches zurück"""
        return [result for result in self.job_results if result.is_worth_processing]

    @property
    def average_rating(self) -> float:
        """Berechnet durchschnittliches Rating"""
        if not self.job_results:
            return 0.0
        average = sum(result.rating for result in self.job_results) / len(self.job_results)
        logger.debug(f"Durchschnittliches Rating berechnet: {average:.2f}")
        return average


@dataclass
class PDFGenerationConfig:
    output_directory: str
    merge_pdfs: bool = True
    include_cover_letters: bool = True
    sort_by_rating: bool = True

    def get_summary_filename(self, timestamp: str) -> str:
        """Erstellt Dateinamen für zusammengefasste PDF"""
        filename = f"job_bewerbungen_{timestamp}.pdf"
        logger.debug(f"PDF-Zusammenfassung Dateiname: {filename}")
        return filename