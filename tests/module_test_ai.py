import os
import sys
from dotenv import load_dotenv

# 1) Dummy-Patch für google.generativeai, damit wir offline testen
import google.generativeai as genai

class DummyGenAI:
    class GenerationConfig:
        def __init__(self, temperature: float):
            self.temperature = temperature
            self.max_output_tokens = None

    class GenerativeModel:
        def __init__(self, model_name: str):
            self.model_name = model_name

        def generate_content(self, prompt: str, generation_config):
            class Response:
                text = f"RESP[{prompt}]"
            return Response()

    @staticmethod
    def configure(api_key: str):
        DummyGenAI._api_key = api_key

genai.configure        = DummyGenAI.configure
genai.GenerationConfig = DummyGenAI.GenerationConfig
genai.GenerativeModel  = DummyGenAI.GenerativeModel

from projekt.backend.core.config       import app_config
from projekt.backend.ai.prompt_manager import PromptManager
from projekt.backend.ai.gemini_client  import GeminiClient
import projekt.backend.ai.text_processor as tp_mod
from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.core.models       import (
    ApplicantProfile, JobDetails, JobSource
)


def test_prompt_manager() -> bool:
    print("=== PromptManager Test ===")
    try:
        pm = PromptManager()
        available = pm.get_available_prompts()
        print("  Available prompts:", available)
        if available:
            sample  = available[0]
            content = pm.get_prompt(sample)
            print(f"  Loaded '{sample}.txt': {len(content)} chars")
        else:
            print("  ⚠️  Keine Prompt-Dateien gefunden (nur Warnung)")
        print("=> PromptManager OK\n")
        return True
    except Exception as e:
        print("!! PromptManager FAILED:", e, "\n")
        return False


def test_gemini_client() -> bool:
    print("=== GeminiClient Test ===")
    # 1) Fehlender API-Key → ValueError
    old_key = app_config.ai.gemini_api_key
    app_config.ai.gemini_api_key = ""
    GeminiClient._initialized = False
    try:
        GeminiClient.generate_content(
            "ping",
            app_config.ai.rating_model.value,
            app_config.ai.rating_temperature
        )
        print("!! Erwarteter Fehler bei fehlendem API-Schlüssel, aber Aufruf erfolgreich")
        return False
    except ValueError as e:
        print("  Fehlender API-Schlüssel korrekt erkannt:", e)

    # 2) Gültiger API-Key → RESP[...] zurück
    app_config.ai.gemini_api_key = "dummy-key"
    GeminiClient._initialized = False
    out = GeminiClient.generate_content(
        "pong",
        app_config.ai.cover_letter_model.value,
        app_config.ai.cover_letter_temperature
    )
    print("  generate_content →", out)
    if not out.startswith("RESP["):
        print("!! Unerwartete Antwort:", out)
        return False

    print("=> GeminiClient OK\n")
    # restore
    app_config.ai.gemini_api_key = old_key
    return True


def test_text_processor() -> bool:
    print("=== TextProcessor Test ===")
    # Patch PromptManager und GeminiClient im text_processor-Modul
    class DummyPM:
        def get_prompt(self, name, **kw):
            return f"[PROMPT:{name}]"

    class DummyGC:
        @classmethod
        def generate_content(cls, prompt, model_type, temperature):
            return f"[OUT:{prompt}|{model_type}|{temperature}]"

    tp_mod.PromptManager = DummyPM
    tp_mod.GeminiClient  = DummyGC

    # Dummy-Objekte statt echter Models
    class DummyJobDetails:
        def __init__(self, raw, fmt=None):
            self.raw_text             = raw
            self.formatted_description = fmt

    class DummyApplicantProfile:
        def to_ai_prompt_format(self):
            return "PROFILE"
        def get_previous_cover_letters(self):
            return ["L1", "L2"]

    try:
        tp   = TextProcessor()
        jd   = DummyJobDetails("raw", "fmt")
        ap   = DummyApplicantProfile()

        out1 = tp.generate_anschreiben(jd, ap)
        print("  generate_anschreiben →", out1)
        out2 = tp.rate_job_match(jd, ap)
        print("  rate_job_match     →", out2)
        out3 = tp.format_job_description("<html>")
        print("  format_job_description →", out3)

        if "[PROMPT:cover_letter_generation]" not in out1:
            print("!! Anschreiben unerwartet:", out1)
            return False
        if "[PROMPT:job_rating]" not in out2:
            print("!! Rating unerwartet:", out2)
            return False
        if "[PROMPT:job_description_formatting]" not in out3:
            print("!! Formatierung unerwartet:", out3)
            return False

        print("=> TextProcessor OK\n")
        return True
    except Exception as e:
        print("!! TextProcessor FAILED:", e, "\n")
        return False


def main():
    load_dotenv()  # falls .env noch nicht geladen
    all_ok = True
    for fn in (test_prompt_manager, test_gemini_client, test_text_processor):
        if not fn():
            all_ok = False
    if all_ok:
        print("🎉 ALLE AI-TESTS ERFOLGREICH")
        sys.exit(0)
    else:
        print("❌ EINIGE AI-TESTS FEHLGESCHLAGEN")
        sys.exit(1)


if __name__ == "__main__":
    main()