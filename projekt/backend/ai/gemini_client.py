import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Wrapper für die Google Gemini API."""

    DEFAULT_API_KEY = 'AIzaSyBI4KCnGbDQi9GGi3MB35lQJ-TSNTQH6oI'  # Besser über .env Datei

    @classmethod
    def get_api_key(cls):
        """Holt den API-Schlüssel aus Umgebungsvariablen oder verwendet den Standard."""
        return os.getenv('GEMINI_API_KEY', cls.DEFAULT_API_KEY)

    @classmethod
    def initialize(cls):
        """Initialisiert die Gemini API."""
        api_key = cls.get_api_key()
        genai.configure(api_key=api_key)

    @staticmethod
    def create_model(model_type='gemini-1.5-flash', temperature=0.5):
        """Erstellt ein Gemini-Modell mit den angegebenen Parametern."""
        model = genai.GenerativeModel(model_type)
        generation_config = genai.GenerationConfig(temperature=temperature)
        return model, generation_config

    @classmethod
    def generate_content(cls, prompt, model_type='gemini-1.5-flash', temperature=0.5):
        """Generiert Inhalt mit dem angegebenen Prompt und Modell."""
        cls.initialize()
        model, generation_config = cls.create_model(model_type, temperature)
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
