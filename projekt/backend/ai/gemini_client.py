import google.generativeai as genai
from typing import Optional
from projekt.backend.core.config import app_config


class GeminiClient:
    """
    Wrapper um google.generativeai; konfiguriert mit api_key aus app_config.
    """

    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        if not cls._initialized:
            api_key = app_config.ai.gemini_api_key
            if not api_key:
                raise ValueError("Gemini API-Schlüssel ist erforderlich")
            genai.configure(api_key=api_key)
            cls._initialized = True

    @classmethod
    def generate_content(
        cls,
        prompt: str,
        model_type: str,
        temperature: float,
        max_tokens: Optional[int] = None
    ) -> str:
        cls._initialize()
        model = genai.GenerativeModel(model_type)
        gen_cfg = genai.GenerationConfig(temperature=temperature)
        if max_tokens is not None:
            gen_cfg.max_output_tokens = max_tokens
        response = model.generate_content(
            prompt, generation_config=gen_cfg
        )
        return response.text or ""