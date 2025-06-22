#!/usr/bin/env python3
"""
Test-Script für projekt.backend.core

Dieses Script importiert alle wichtigen Komponenten des core-Pakets,
initialisiert das Logging und führt einfache Smoke-Tests durch.
"""

import sys
import logging

# Importiere aus deinem Core-Paket
from projekt.backend.core import (
    JobSource,
    AIModel,
    SearchCriteria,
    ApplicantProfile,
    JobDetails,
    JobMatchResult,
    ScrapingSession,
    PDFGenerationConfig,
    Site,
    PathConfig,
    AIConfig,
    ScrapingConfig,
    LoggingConfig,
    AppConfig,
    USER_AGENTS,
    SITE_CONFIGS,
    get_site_config,
    get_site_config_by_string,
    setup_logging,
    app_config,
)

logger = logging.getLogger(__name__)


def test_enums():
    print("== Enums ==")
    print(" JobSource:", [e.value for e in JobSource])
    print(" AIModel:", [e.value for e in AIModel])
    print(" Site:", [e.value for e in Site])
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

    # Site-Konfiguration
    print("== SITE_CONFIGS Test ==")
    for site in Site:
        cfg = get_site_config(site)
        print(f" {site.value} → base_url={cfg['base_url']}")
    by_str = get_site_config_by_string("Xing")
    print(" get_site_config_by_string('Xing'): base_url=", by_str["base_url"])
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
    # JobDetails
    job = JobDetails(
        title="Praktikant Data Science (m/w/d)",
        title_clean="",
        raw_text="Ein Test-Job",
        url="https://example.com/job",
        source_site=JobSource.STEPSTONE,
    )
    print(" JobDetails.title_clean:", job.title_clean)
    print(" safe_filename:", job.safe_filename)
    print(" enthält Praktikum?:", job.contains_internship_keywords())
    # JobMatchResult
    match = JobMatchResult(job, rating=7, formatted_description="Desc", cover_letter=None, ai_model_used="FLASH")
    print(" JobMatchResult.rating:", match.rating)
    print(" is_worth_processing:", match.is_worth_processing)
    print(" needs_premium_model:", match.needs_premium_model)
    print(" PDF-Filename:", match.get_pdf_filename())
    # ScrapingSession
    session = ScrapingSession(crit, prof, JobSource.STEPSTONE, total_jobs_found=3)
    for i in range(3):
        r = JobMatchResult(
            JobDetails(f"Job{i}", f"Job{i}", "Raw", "url"),
            rating=i * 3 + 2,
            formatted_description="fmt"
        )
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