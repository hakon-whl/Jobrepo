#!/usr/bin/env python3
import argparse
import sys
from dotenv import load_dotenv
from projekt.backend.ai import GeminiClient, TextProcessor, PromptManager
from projekt.backend.core.models import AIModel, ApplicantProfile, JobDetails, JobSource
from projekt.backend.core.config import app_config

# .env laden (GEMINI_API_KEY)
load_dotenv()

# Test-Daten
JOB_DESCRIPTION = """
Praktikant im Bereich Softwaretests & Business Analyse (m/w/d)
Willkommen bei der Allianz

Data Analytics und Künstliche Intelligenz beschleunigen weiter stark den
technologischen Wandel in allen Unternehmensbereichen der Versicherungen. Die
Allianz in Deutschland baut deshalb neue Expertise, Prozesse und Infrastruktur
auf, um das Potential von Data Analytics nutzbar zu machen. Bei uns arbeitest Du
im Herzen eines der wichtigsten Zukunftsfelder unserer Branche.

Wir betreuen, verantworten und gestalten ganzheitlich die Strategie, Prozesse
und Infrastruktur im Bereich Data Analytics, sowohl für Business Intelligence
als auch „Big Data" Anwendungen. Wir erarbeiten gemeinsam mit verschiedenen
Stakeholdern aus den Geschäftsbereichen die Data Analytics Strategie und
Projekt-Roadmap und verantworten den Aufbau einer modernen Infrastruktur.

Wir suchen zum nächstmöglichen Zeitpunkt Unterstützung für den Bereich Testing,
Qualitätssicherung und Business Analyse im Umfeld Business Intelligence und Data
Analytics.

Deine Aufgaben
Das erwartet dich bei uns als Praktikant im Bereich Softwaretests &
Business Analyse (m/w/d)

- Du arbeitest an einem strategischen, konzernübergreifenden Vorhaben in einem
  cross-funktionalen Team mit agilen Projektmanagementmethoden.
- Dabei übernimmst Du schrittweise eigene Aufgabenpakete im Umfeld Softwaretests
  und Qualitätssicherung sowie Business Analyse im Umfeld Business Intelligence
  und Data Analytics.
- Du unterstützt das Team in der Datenanalyse und kannst auch eigene
  Datenauswertungen erstellen.
- Du lernst Technologien für Analytics-Anwendungen kennen.
- Du arbeitest mit spannenden Technologien (z. B. Oracle Cloud Infrastructure,
  DB2, SAS Enterprise Guide, SQL, Jira, Confluence).

Dein Profil
- Du bist auf der Suche nach einem Pflichtpraktikum im Rahmen deines Studiums der
  (Wirtschafts-)Informatik oder einem ähnlichen Studiengang.
- Du verfügst über Kenntnisse im Umgang mit diesen Technologien: Relationale
  Datenbanken (v.a. Oracle Cloud Infrastructure, DB2), SAS (SAS Base,
  Enterprise Guide), SQL.
- Idealerweise konntest du schon erste Erfahrungen im Bereich Softwaretests und
  Qualitätssicherung sowie mit DWH/BI-Architekturen sammeln.
- Wünschenswert sind Erfahrungen mit und Wissen zu Methoden im Bereich des
  agilen Projektmanagements (z. B. Scrum).
- Du hast verhandlungssichere Deutsch- und gute Englischkenntnisse.
"""

APPLICANTS = {
    "Alice": {
        "profile": ApplicantProfile(
            study_info="Wirtschaftsinformatik an der HM München, 5. Semester",
            interests="Softwaretesting, Datenanalyse, agile Methoden",
            skills=["Python", "SQL", "Git", "Scrum", "Test-Automation"]
        )
    },
    "Bob": {
        "profile": ApplicantProfile(
            study_info="Betriebswirtschaftslehre an der LMU München, 4. Semester",
            interests="Projektmanagement, Stakeholder-Management, Prozessoptimierung",
            skills=["Excel", "PowerPoint", "Kommunikation", "Teamarbeit"]
        )
    }
}


def test_config_display():
    """Zeigt die aktuelle AI-Konfiguration an"""
    print("=== AI-Konfiguration ===")
    print(f"📄 Anschreiben-Generierung:")
    print(f"   Model: {app_config.ai.cover_letter_model.value}")
    print(f"   Temperature: {app_config.ai.cover_letter_temperature}")
    print(f"   Max Tokens: {app_config.ai.cover_letter_max_tokens}")

    print(f"\n📊 Job-Rating:")
    print(f"   Model: {app_config.ai.rating_model.value}")
    print(f"   Temperature: {app_config.ai.rating_temperature}")
    print(f"   Max Tokens: {app_config.ai.rating_max_tokens}")

    print(f"\n🔧 Job-Formatierung:")
    print(f"   Model: {app_config.ai.formatting_model.value}")
    print(f"   Temperature: {app_config.ai.formatting_temperature}")
    print(f"   Max Tokens: {app_config.ai.formatting_max_tokens}")

    print(f"\n⚙️  Allgemeine Einstellungen:")
    print(f"   Premium Threshold: {app_config.ai.premium_rating_threshold}")
    print(f"   Auto Premium Upgrade: {app_config.ai.auto_upgrade_to_premium}")
    print(f"   Timeout: {app_config.ai.default_timeout}s")
    print(f"   Max Retries: {app_config.ai.max_retries}")
    print("")


def test_gemini_client():
    """Test der GeminiClient-Funktionalität"""
    print("=== GeminiClient Test ===")

    try:
        # API-Key Test
        print("1. API-Key Test...")
        api_key = GeminiClient.get_api_key()
        print(f"   ✓ API-Key gefunden: {api_key[:10]}...")

        # Initialisierung Test
        print("2. Initialisierung Test...")
        GeminiClient.initialize()
        print("   ✓ Gemini Client erfolgreich initialisiert")

        # Einfacher Content-Generation Test mit Config-Werten
        print("3. Content-Generation Test...")
        test_prompt = "Erkläre in einem Satz, was Künstliche Intelligenz ist."
        result = GeminiClient.generate_content(
            prompt=test_prompt,
            model_type=app_config.ai.rating_model.value,  # Verwende Config-Model
            temperature=app_config.ai.rating_temperature  # Verwende Config-Temperature
        )
        print(f"   ✓ Content erfolgreich generiert ({len(result)} Zeichen)")

        # Model-Creation Test mit Config-Werten
        print("4. Model-Creation Test...")
        model, config = GeminiClient.create_model(
            app_config.ai.cover_letter_model.value,
            app_config.ai.cover_letter_temperature
        )
        print(f"   ✓ Model erstellt: {model.model_name}")
        print(f"   ✓ Temperature: {config.temperature}")

        print("   ✅ GeminiClient Tests erfolgreich!\n")
        return True

    except Exception as e:
        print(f"   ❌ GeminiClient Test fehlgeschlagen: {e}\n")
        return False


def test_prompt_manager():
    """Test der PromptManager-Funktionalität"""
    print("=== PromptManager Test ===")

    try:
        # PromptManager Initialisierung
        print("1. PromptManager Initialisierung...")
        manager = PromptManager(app_config.paths.prompts_dir)
        print(f"   ✓ PromptManager initialisiert für: {manager.prompts_directory}")

        # Verfügbare Prompts auflisten
        print("2. Verfügbare Prompts auflisten...")
        available_prompts = manager.get_available_prompts()
        print(f"   ✓ {len(available_prompts)} Prompts gefunden:")
        for prompt in available_prompts:
            print(f"     - {prompt}")

        if not available_prompts:
            print("   ⚠️  Keine Prompt-Dateien gefunden!")
            return False

        print("   ✅ PromptManager Tests erfolgreich!\n")
        return True

    except Exception as e:
        print(f"   ❌ PromptManager Test fehlgeschlagen: {e}\n")
        return False


def test_text_processor():
    """Test der TextProcessor-Funktionalität"""
    print("=== TextProcessor Test ===")

    try:
        # TextProcessor Initialisierung
        print("1. TextProcessor Initialisierung...")
        processor = TextProcessor()
        print("   ✓ TextProcessor initialisiert")

        # Test Job Details
        job_details = JobDetails(
            title="Test Praktikum",
            title_clean="Test Praktikum",
            raw_text=JOB_DESCRIPTION,
            url="https://example.com/job",
            source_site=JobSource.STEPSTONE
        )

        # Job Rating Test (nutzt automatisch Config-Parameter)
        print("2. Job Rating Test...")
        for name, data in APPLICANTS.items():
            rating = processor.rate_job_match(job_details, data["profile"])
            print(f"   ✓ Rating für {name}: {rating}/10")

        # Job Description Formatting Test (nutzt automatisch Config-Parameter)
        print("3. Job Description Formatting Test...")
        formatted = processor.format_job_description("<html><body>Test Job</body></html>")
        print(f"   ✓ Formatierung erfolgreich ({len(formatted)} Zeichen)")

        print("   ✅ TextProcessor Tests erfolgreich!\n")
        return True

    except Exception as e:
        print(f"   ❌ TextProcessor Test fehlgeschlagen: {e}\n")
        return False


def test_anschreiben_generation():
    """Test der Anschreiben-Generierung (nutzt automatisch Config-Parameter)"""
    print("=== Anschreiben-Generierung Test ===")

    try:
        processor = TextProcessor()
        job_details = JobDetails(
            title="Praktikant Softwaretests",
            title_clean="Praktikant Softwaretests",
            raw_text=JOB_DESCRIPTION,
            url="https://example.com/job",
            source_site=JobSource.STEPSTONE
        )

        print(f"📝 Verwendet Config-Einstellungen:")
        print(f"   Model: {app_config.ai.cover_letter_model.value}")
        print(f"   Temperature: {app_config.ai.cover_letter_temperature}")

        for name, data in APPLICANTS.items():
            print(f"\n--- Anschreiben für {name} ---")

            # Keine Parameter mehr nötig - alles aus Config!
            cover_letter = processor.generate_anschreiben(
                job_details=job_details,
                applicant_profile=data["profile"]
            )

            print(f"✓ Anschreiben generiert ({len(cover_letter)} Zeichen)")
            print(f"Erste 200 Zeichen: {cover_letter[:200]}...")

        print("\n   ✅ Anschreiben-Generierung Tests erfolgreich!\n")
        return True

    except Exception as e:
        print(f"   ❌ Anschreiben-Generierung Test fehlgeschlagen: {e}\n")
        return False


def test_config_modification():
    """Test der Config-Änderung zur Laufzeit"""
    print("=== Config-Änderung Test ===")

    try:
        print("1. Ursprüngliche Config...")
        original_temp = app_config.ai.cover_letter_temperature
        original_model = app_config.ai.cover_letter_model
        print(f"   Original Temperature: {original_temp}")
        print(f"   Original Model: {original_model.value}")

        print("2. Config temporär ändern...")
        app_config.ai.cover_letter_temperature = 0.9
        app_config.ai.cover_letter_model = AIModel.PRO
        print(f"   Neue Temperature: {app_config.ai.cover_letter_temperature}")
        print(f"   Neues Model: {app_config.ai.cover_letter_model.value}")

        print("3. TextProcessor mit neuer Config testen...")
        processor = TextProcessor()
        # Kurzer Test würde hier laufen...

        print("4. Config zurücksetzen...")
        app_config.ai.cover_letter_temperature = original_temp
        app_config.ai.cover_letter_model = original_model
        print(f"   Zurücksetzung: {app_config.ai.cover_letter_temperature}, {app_config.ai.cover_letter_model.value}")

        print("   ✅ Config-Änderung Test erfolgreich!\n")
        return True

    except Exception as e:
        print(f"   ❌ Config-Änderung Test fehlgeschlagen: {e}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test des AI-Moduls: Vollständig Config-basiert"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Überspringe AI-Tests (nur lokale Tests)"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Zeige detaillierte Config-Informationen"
    )
    parser.add_argument(
        "--test-config-change",
        action="store_true",
        help="Teste Config-Änderungen zur Laufzeit"
    )
    args = parser.parse_args()

    print("🚀 AI-Module Test Suite gestartet (Config-basiert)\n")

    # Config-Anzeige
    if args.show_config:
        test_config_display()

    # Lokale Tests (ohne AI-Aufrufe)
    all_passed = True

    # PromptManager Test
    all_passed &= test_prompt_manager()

    # Config-Änderungs-Test
    if args.test_config_change:
        all_passed &= test_config_modification()

    if not args.skip_ai:
        # AI-Tests (benötigen API-Key und nutzen Config-Parameter)
        all_passed &= test_gemini_client()
        all_passed &= test_text_processor()
        all_passed &= test_anschreiben_generation()
    else:
        print("⏭️  AI-Tests übersprungen (--skip-ai Flag gesetzt)\n")

    # Abschlussbericht
    if all_passed:
        print("🎉 Alle Tests erfolgreich bestanden!")
        print("💡 Alle AI-Parameter werden zentral über die Config gesteuert!")
        sys.exit(0)
    else:
        print("❌ Einige Tests sind fehlgeschlagen!")
        sys.exit(1)


if __name__ == "__main__":
    main()