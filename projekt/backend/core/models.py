from dataclasses import dataclass, field
from typing import Dict, List, Any
import re
from projekt.backend.core.config import app_config, JobSource, AIModel

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

@dataclass
class ApplicantProfile:
    study_info: str
    interests: str
    skills: List[str]
    pdf_contents: Dict[str, str] = field(default_factory=dict)

    def to_ai_prompt_format(self) -> str:
        skills_text = ", ".join(self.skills) if self.skills else "Keine Skills angegeben"
        profile_text = f"""Studium: {self.study_info}
        Interessen: {self.interests}
        Fähigkeiten: {skills_text}"""
        return profile_text

    def get_previous_cover_letters(self) -> str:
        if not self.pdf_contents:
            return ""
        combined_letters = "\n\n".join(self.pdf_contents.values())
        return combined_letters

@dataclass
class JobDetailsScraped:
    title: str
    raw_text: str
    url: str
    source: JobSource
    is_internship: bool = field(init=False)

    def __post_init__(self):
        keys = ["praktikant", "praktikum", "intern", "trainee", "werkstudent"]
        self.is_internship = any(k in self.title.lower() for k in keys)

@dataclass
class JobDetailsAi:
    scraped: JobDetailsScraped
    rating: int
    formatted_text: str
    cover_letters: str
    ai_model_used: AIModel

    def get_output_filename(self) -> str:
        raw = f"{self.rating}_{self.scraped.title}"
        safe = re.sub(r"[^0-9A-Za-z_-]+", "_", raw)
        safe = re.sub(r"_+", "_", safe).strip("_")
        max_len = 100
        safe = safe[:max_len]
        return f"{safe}.pdf"

@dataclass
class ScrapingSession:
    search_criteria: SearchCriteria
    applicant_profile: ApplicantProfile
    selected_source: JobSource
    scraped_jobs: List[JobDetailsScraped]
    ai_jobs: List[JobDetailsAi]

    @property
    def total_found(self) -> int:
        return len(self.scraped_jobs)

    @property
    def total_processed(self) -> int:
        return len(self.ai_jobs)