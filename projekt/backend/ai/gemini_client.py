import google.generativeai as genai
import logging
from projekt.backend.core.config import app_config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper für die Google Gemini API."""

    @classmethod
    def get_api_key(cls) -> str:
        """Holt den API-Schlüssel aus der Konfiguration."""
        api_key = app_config.ai.gemini_api_key
        if not api_key:
            logger.error("Kein Gemini API-Schlüssel konfiguriert")
            raise ValueError("Gemini API-Schlüssel ist erforderlich")

        logger.debug("API-Schlüssel erfolgreich abgerufen")
        return api_key

    @classmethod
    def initialize(cls) -> None:
        """Initialisiert die Gemini API."""
        try:
            api_key = cls.get_api_key()
            genai.configure(api_key=api_key)
            logger.info("Gemini API erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler bei Gemini API-Initialisierung: {e}")
            raise

    @staticmethod
    def create_model(model_type: str, temperature: float):
        """Erstellt ein Gemini-Modell mit den angegebenen Parametern."""
        try:
            model = genai.GenerativeModel(model_type)
            generation_config = genai.GenerationConfig(temperature=temperature)
            logger.debug(f"Gemini-Modell erstellt: {model_type} (Temperatur: {temperature})")
            return model, generation_config
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Gemini-Modells: {e}")
            raise

    @classmethod
    def generate_content(cls, prompt: str, model_type: str, temperature: float) -> str:
        """Generiert Inhalt mit dem angegebenen Prompt und Modell."""
        try:
            cls.initialize()
            model, generation_config = cls.create_model(model_type, temperature)

            logger.info(f"Generiere Inhalt mit Modell {model_type}")
            logger.debug(f"Prompt-Länge: {len(prompt)} Zeichen")

            response = model.generate_content(prompt, generation_config=generation_config)

            if not response.text:
                logger.warning("Leere Antwort von Gemini API erhalten")
                return ""

            logger.info(f"Inhalt erfolgreich generiert: {len(response.text)} Zeichen")
            return response.text

        except Exception as e:
            logger.error(f"Fehler bei der Inhaltsgenerierung: {e}")
            raise