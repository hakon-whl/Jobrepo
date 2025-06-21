import logging
from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.ai.prompt_manager import PromptManager
from projekt.backend.core.models import ApplicantProfile, JobDetails, AIModel
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)


class TextProcessor:
    """Verarbeitet Text mit AI-Unterstützung"""

    def __init__(self):
        self.prompt_manager = PromptManager(app_config.paths.prompts_dir)
        logger.info("TextProcessor initialisiert")

    def generate_anschreiben(
            self,
            job_details: JobDetails,
            applicant_profile: ApplicantProfile,
            ai_model: AIModel = AIModel.FLASH
    ) -> str:
        """Generiert ein Anschreiben basierend auf JobDetails und ApplicantProfile."""
        try:
            logger.info(f"Generiere Anschreiben für Job: {job_details.title}")

            prompt = self.prompt_manager.get_prompt(
                "cover_letter_generation",
                job_description=job_details.formatted_description or job_details.raw_text,
                applicant_profile=applicant_profile.to_ai_prompt_format(),
                previous_cover_letters=applicant_profile.get_previous_cover_letters()
            )

            cover_letter = GeminiClient.generate_content(
                prompt=prompt,
                model_type=ai_model.value,
                temperature=app_config.ai.default_temperature
            )

            logger.info(f"Anschreiben erfolgreich generiert: {len(cover_letter)} Zeichen")
            return cover_letter

        except Exception as e:
            logger.error(f"Fehler bei Anschreiben-Generierung für {job_details.title}: {e}")
            raise

    def rate_job_match(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> int:
        """Bewertet die Übereinstimmung zwischen Job und Bewerber (1-10)."""
        try:
            logger.info(f"Bewerte Job-Match für: {job_details.title}")

            prompt = self.prompt_manager.get_prompt(
                "job_rating",
                applicant_profile=applicant_profile.to_ai_prompt_format(),
                job_description=job_details.formatted_description or job_details.raw_text
            )

            result = GeminiClient.generate_content(
                prompt=prompt,
                model_type=AIModel.FLASH_2.value,
                temperature=app_config.ai.rating_temperature
            )

            try:
                rating = int(result.strip())
                logger.info(f"Job-Rating für '{job_details.title}': {rating}/10")
                return rating
            except (ValueError, TypeError):
                logger.error(f"Konnte Rating nicht parsen: {result}")
                return 0

        except Exception as e:
            logger.error(f"Fehler bei Job-Rating für {job_details.title}: {e}")
            return 0

    def format_job_description(self, html_code: str) -> str:
        """Formatiert Jobbeschreibungen in strukturiertes Markdown."""
        try:
            logger.info("Formatiere Job-Beschreibung")
            logger.debug(f"Input-Länge: {len(html_code)} Zeichen")

            prompt = self.prompt_manager.get_prompt(
                "job_description_formatting",
                html_code=html_code
            )

            formatted_description = GeminiClient.generate_content(
                prompt=prompt,
                model_type=AIModel.FLASH_2.value,
                temperature=0.2
            )

            logger.info(f"Job-Beschreibung erfolgreich formatiert: {len(formatted_description)} Zeichen")
            return formatted_description

        except Exception as e:
            logger.error(f"Fehler bei Job-Beschreibung-Formatierung: {e}")
            raise