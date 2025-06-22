import logging
from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.ai.prompt_manager import PromptManager
from projekt.backend.core.models import ApplicantProfile, JobDetails
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)


class TextProcessor:
    def __init__(self):
        self.prompt_manager = PromptManager(app_config.paths.prompts_dir)

        # Log der verwendeten Konfiguration
        logger.info("TextProcessor initialisiert mit AI-Config:")
        logger.info(f"  Anschreiben-Model: {app_config.ai.cover_letter_model.value}")
        logger.info(f"  Rating-Model: {app_config.ai.rating_model.value}")
        logger.info(f"  Formatierung-Model: {app_config.ai.formatting_model.value}")

    def generate_anschreiben(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> str:
        """
        Generiert Anschreiben basierend auf AUSSCHLIESSLICH Config-Parametern
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                "cover_letter_generation",
                job_description=job_details.formatted_description or job_details.raw_text,
                applicant_profile=applicant_profile.to_ai_prompt_format(),
                previous_cover_letters=applicant_profile.get_previous_cover_letters()
            )

            logger.debug(f"Anschreiben-Generierung mit Model: {app_config.ai.cover_letter_model.value}, "
                         f"Temperature: {app_config.ai.cover_letter_temperature}")

            return GeminiClient.generate_content(
                prompt=prompt,
                model_type=app_config.ai.cover_letter_model.value,
                temperature=app_config.ai.cover_letter_temperature
            )
        except Exception as e:
            logger.error(f"Anschreiben-Generierung Fehler: {e}")
            raise

    def rate_job_match(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> int:
        """
        Bewertet Job-Match basierend auf AUSSCHLIESSLICH Config-Parametern
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                "job_rating",
                applicant_profile=applicant_profile.to_ai_prompt_format(),
                job_description=job_details.formatted_description or job_details.raw_text
            )

            logger.debug(f"Job-Rating mit Model: {app_config.ai.rating_model.value}, "
                         f"Temperature: {app_config.ai.rating_temperature}")

            result = GeminiClient.generate_content(
                prompt=prompt,
                model_type=app_config.ai.rating_model.value,
                temperature=app_config.ai.rating_temperature
            )

            rating = int(result.strip())
            logger.info(f"Job-Rating Ergebnis: {rating}/10")
            return rating

        except Exception as e:
            logger.error(f"Job-Rating Fehler: {e}")
            return 0

    def format_job_description(self, html_code: str) -> str:
        """
        Formatiert Job-Beschreibung basierend auf AUSSCHLIESSLICH Config-Parametern
        """
        try:
            prompt = self.prompt_manager.get_prompt("job_description_formatting", html_code=html_code)

            logger.debug(f"Job-Formatierung mit Model: {app_config.ai.formatting_model.value}, "
                         f"Temperature: {app_config.ai.formatting_temperature}")

            return GeminiClient.generate_content(
                prompt=prompt,
                model_type=app_config.ai.formatting_model.value,
                temperature=app_config.ai.formatting_temperature
            )
        except Exception as e:
            logger.error(f"Job-Formatierung Fehler: {e}")
            raise