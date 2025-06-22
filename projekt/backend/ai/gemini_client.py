import google.generativeai as genai
import logging
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)


class GeminiClient:
    @classmethod
    def get_api_key(self) -> str:
        api_key = app_config.ai.gemini_api_key
        if not api_key:
            raise ValueError("Gemini API-Schlüssel ist erforderlich")
        return api_key

    @classmethod
    def initialize(self) -> None:
        api_key = self.get_api_key()
        genai.configure(api_key=api_key)

    @staticmethod
    def create_model(model_type: str, temperature: float):
        model = genai.GenerativeModel(model_type)
        generation_config = genai.GenerationConfig(temperature=temperature)
        return model, generation_config

    @classmethod
    def generate_content(self, prompt: str, model_type: str, temperature: float) -> str:
        try:
            self.initialize()
            model, generation_config = self.create_model(model_type, temperature)
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text or ""
        except Exception as e:
            logger.error(f"AI Content-Generierung Fehler: {e}")
            raise