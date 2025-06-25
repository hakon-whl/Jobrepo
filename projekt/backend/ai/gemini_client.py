import google.generativeai as genai
from projekt.backend.core.config import app_config


class GeminiClient:

    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        if not cls._initialized:
            key = app_config.ai.gemini_api_key
            print(key)
            if not key:
                raise ValueError("Gemini API-Schlüssel ist erforderlich (ENV GEMINI_API_KEY)")
            genai.configure(api_key=key)
            cls._initialized = True

    @classmethod
    def generate_content(cls, prompt: str, model_type: str, temperature: float) -> str:
        cls._initialize()
        model = genai.GenerativeModel(model_type)
        cfg = genai.GenerationConfig(temperature=temperature)
        response = model.generate_content(
            prompt,
            generation_config=cfg
        )
        return response.text or ""