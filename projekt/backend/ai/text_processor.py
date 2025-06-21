import logging
from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.ai.prompt_manager import PromptManager
from projekt.backend.core.models import ApplicantProfile, JobDetails, AIModel
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)


class TextProcessor:
    def __init__(self):
        self.prompt_manager = PromptManager(app_config.paths.prompts_dir)

    def generate_anschreiben(self, job_details: JobDetails, applicant_profile: ApplicantProfile,
                           ai_model: AIModel = AIModel.FLASH) -> str:
        try:
            prompt = self.prompt_manager.get_prompt(
                "cover_letter_generation",
                job_description=job_details.formatted_description or job_details.raw_text,
                applicant_profile=applicant_profile.to_ai_prompt_format(),
                previous_cover_letters=applicant_profile.get_previous_cover_letters()
            )

            return GeminiClient.generate_content(
                prompt=prompt,
                model_type=ai_model.value,
                temperature=app_config.ai.default_temperature
            )
        except Exception as e:
            logger.error(f"Anschreiben-Generierung Fehler: {e}")
            raise

    def rate_job_match(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> int:
        try:
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

            return int(result.strip())
        except Exception as e:
            logger.error(f"Job-Rating Fehler: {e}")
            return 0

    def format_job_description(self, html_code: str) -> str:
        try:
            prompt = self.prompt_manager.get_prompt("job_description_formatting", html_code=html_code)
            return GeminiClient.generate_content(
                prompt=prompt,
                model_type=AIModel.FLASH_2.value,
                temperature=0.2
            )
        except Exception as e:
            logger.error(f"Job-Formatierung Fehler: {e}")
            raise