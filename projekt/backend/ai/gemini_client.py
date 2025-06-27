import google.generativeai as genai
from projekt.backend.core.config import app_config
from projekt.backend.core.models import AIModel

class GeminiClient:
    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        if not cls._initialized:
            api_key = app_config.ai.gemini_api_key
            if not api_key:
                raise ValueError(
                    "Gemini API-Schlüssel ist erforderlich. "
                    "Stelle sicher dass api_key.txt existiert und nicht leer ist."
                )

            genai.configure(api_key=api_key)
            cls._initialized = True

    @classmethod
    def generate_content(cls, prompt: str, model_type: str, temperature: float) -> str:
        cls._initialize()

        model = genai.GenerativeModel(model_type)
        config = genai.GenerationConfig(temperature=temperature)

        response = model.generate_content(prompt, generation_config=config)
        return response.text or ""

    @classmethod
    def generate_content_with_model(cls, prompt: str, model: AIModel, temperature: float) -> str:
        return cls.generate_content(prompt, model.value, temperature)