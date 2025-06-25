from projekt.backend.ai.prompt_manager import PromptManager
from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.core.config import app_config
from projekt.backend.core.models import ApplicantProfile, JobDetails


class TextProcessor:

    def __init__(self):
        self.pm = PromptManager()

    def generate_anschreiben(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> str:
        prompt = self.pm.get_prompt(
            "cover_letter_generation",
            job_description=(
                job_details.formatted_description
                or job_details.raw_text
            ),
            applicant_profile=applicant_profile.to_ai_prompt_format(),
            previous_cover_letters=applicant_profile.get_previous_cover_letters()
        )
        return GeminiClient.generate_content(
            prompt=prompt,
            model_type=app_config.ai.cover_letter_model.value,
            temperature=app_config.ai.cover_letter_temperature
        )

    def rate_job_match(self, job_details: JobDetails, applicant_profile: ApplicantProfile) -> int:
        prompt = self.pm.get_prompt(
            "job_rating",
            applicant_profile=applicant_profile.to_ai_prompt_format(),
            job_description=(
                job_details.formatted_description
                or job_details.raw_text
            )
        )
        res = GeminiClient.generate_content(
            prompt=prompt,
            model_type=app_config.ai.rating_model.value,
            temperature=app_config.ai.rating_temperature
        )
        try:
            return int(res.strip())
        except ValueError:
            return 0

    def format_job_description(self, html_code: str) -> str:
        prompt = self.pm.get_prompt(
            "job_description_formatting",
            html_code=html_code
        )
        return GeminiClient.generate_content(
            prompt=prompt,
            model_type=app_config.ai.formatting_model.value,
            temperature=app_config.ai.formatting_temperature
        )