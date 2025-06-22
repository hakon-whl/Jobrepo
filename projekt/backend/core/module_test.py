#!/usr/bin/env python3
"""
Test-Script für projekt.backend.core

Dieses Script importiert alle wichtigen Komponenten des core-Pakets,
initialisiert das Logging und führt einfache Smoke-Tests durch.
"""

import sys
import logging

from projekt.backend.core import (
    JobSource,
    AIModel,
    SearchCriteria,
    ApplicantProfile,
    JobDetails,
    JobMatchResult,
    ScrapingSession,
    PDFGenerationConfig,
    PathConfig,
    AIConfig,
    ScrapingConfig,
    LoggingConfig,
    AppConfig,
    USER_AGENTS,
    SITE_CONFIGS,
    get_site_config_by_string,
    setup_logging,
    app_config,
)

logger = logging.getLogger(__name__)


def test_enums():
    print("== Enums ==")
    print(" JobSource:", [e.value for e in JobSource])
    print(" AIModel:", [e.value for e in AIModel])
    print()


def test_config():
    print("== Konfiguration ==")
    # Pfade
    paths: PathConfig = app_config.paths
    print(" Frontend-Dir:", paths.frontend_dir)
    print(" Build-Dir:", paths.build_dir)
    print(" Temp-PDFs-Dir:", paths.temp_pdfs_dir)
    # AI
    ai: AIConfig = app_config.ai
    print(" AI-Key (Anfang):", ai.gemini_api_key[:8], "…")
    print(" CoverLetter-Model:", ai.cover_letter_model.value)
    print(" CoverLetter-Temp:", ai.cover_letter_temperature)
    print(" Rating-Model:", ai.rating_model.value)
    print(" Rating-Temp:", ai.rating_temperature)
    # Scraping
    sc: ScrapingConfig = app_config.scraping
    print(" Max-Pages/Site:", sc.max_pages_per_site)
    print(" Max-Jobs/Session:", sc.max_jobs_per_session)
    # Logging
    lc: LoggingConfig = app_config.logging_config
    print(" Log-Level:", lc.level)
    print()

    # SITE_CONFIGS Test
    print("== SITE_CONFIGS Test ==")
    for js in JobSource:
        cfg = SITE_CONFIGS.get(js)
        print(f" {js.value} → base_url={cfg.get('base_url') if cfg else 'kein Eintrag'}")
    # get_site_config_by_string
    for name in ["StepStone", "Xing", "Stellenanzeigen", "Stellenanzeigen.de"]:
        cfg = get_site_config_by_string(name)
        print(f" get_site_config_by_string('{name}'): base_url={cfg.get('base_url') if cfg else 'None'}")
    print()


def test_models():
    print("== Datenmodelle ==")
    # SearchCriteria
    crit = SearchCriteria("Python Developer", "München", "25", discipline="IT")
    print(" SearchCriteria:", crit)
    print("  to_stepstone_params:", crit.to_stepstone_params())

    # ApplicantProfile
    prof = ApplicantProfile(
        study_info="WI an der HM München, 5. Sem.",
        interests="ML, Web Dev",
        skills=["Python", "SQL"],
        pdf_contents={"a.pdf": "Anschreiben A"}
    )
    print(" ApplicantProfile AI-Format:\n", prof.to_ai_prompt_format())
    print(" Previous letters:", prof.get_previous_cover_letters())

    # JobDetails: Test für verschiedene Titel
    test_titles = [
        ("Praktikum Data Science (m/w/d)", True),
        ("Werkstudent Backend-Entwicklung", True),
        ("Internship Frontend Developer", True),
        ("HiWi KI Projekt", True),
        ("Student Assistant Marketing", True),
        ("Data Engineer", False),
        ("Trainee Sales Manager", True),
        ("Ferienjob Lager", False),
    ]
    for title, expected in test_titles:
        job = JobDetails(
            title=title,
            title_clean="",
            raw_text="Test",
            url="http://example.com",
            source_site=JobSource.STEPSTONE
        )
        print(f" '{title}': is_internship={job.is_internship} (erwartet: {expected})")

    # Safe filename
    job = JobDetails("Praktikant: Entwicklung/IT", "", "X", "u", JobSource.XING)
    print(" safe_filename:", job.safe_filename)

    # JobMatchResult
    match = JobMatchResult(job, rating=7, formatted_description="Desc", cover_letter=None, ai_model_used="FLASH")
    print(" JobMatchResult.rating:", match.rating)
    print(" is_worth_processing:", match.is_worth_processing)
    print(" needs_premium_model:", match.needs_premium_model)
    print(" PDF-Filename:", match.get_pdf_filename())

    # ScrapingSession
    session = ScrapingSession(crit, prof, JobSource.XING, total_jobs_found=3)
    for i in range(3):
        jd = JobDetails(f"Job{i}", f"Job{i}", "Raw", "url", JobSource.STEPSTONE)
        r = JobMatchResult(jd, rating=i * 3 + 2, formatted_description="fmt")
        session.add_result(r)
    print(" Session total_jobs_processed:", session.total_jobs_processed)
    print(" successful_matches:", len(session.successful_matches))
    print(" average_rating:", session.average_rating)

    # PDFGenerationConfig
    pdf_cfg = PDFGenerationConfig(output_directory="./out")
    print(" PDF summary filename:", pdf_cfg.get_summary_filename("20250622_123456"))
    print()


def main():
    # Logging initialisieren
    setup_logging(app_config.logging_config, app_config.paths.logs_dir)
    logger.info("Starte Core-Paket Test")

    try:
        test_enums()
        test_config()
        test_models()
        print("🎉 Alle Tests erfolgreich abgeschlossen!")
        return 0
    except Exception as e:
        logger.error("Fehler im Test-Script", exc_info=e)
        print("❌ Test-Script abgebrochen:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())