#!/usr/bin/env python3
import argparse
from dotenv import load_dotenv
from projekt.backend.ai import GeminiClient, TextProcessor

# .env laden (GEMINI_API_KEY)
load_dotenv()

# 1) Stellenbeschreibung (Plain-Text)
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

# 2) Zwei verschiedene Bewerberprofile
APPLICANTS = {
    "Alice": {
        "discipline": """
Name: Alice Schmidt
Studium: Wirtschaftsinformatik an der HM München
Skills: Python, SQL, Datenanalyse, automatisiertes Testing
Erfahrung: Praktikum im Bereich Softwaretest bei Musterfirma AG
Interessen: agile Methoden, Continuous Integration/Delivery
""",
        "previous": ""
    },
    "Bob": {
        "discipline": """
Name: Bob Müller
Studium: Betriebswirtschaftslehre an der LMU München
Skills: Projektmanagement, Marketing, Kommunikation
Erfahrung: Werkstudent im Marketing bei Handelsunternehmen GmbH
Interessen: Stakeholder-Management, Prozessoptimierung
""",
        "previous": ""
    }
}


def main():
    parser = argparse.ArgumentParser(
        description="Test des AI-Moduls: Anschreiben & Job-Fit"
    )
    parser.add_argument(
        "--model",
        default="gemini-1.5-flash",
        help="Gemini-Modell (z.B. gemini-2.0-flash)"
    )
    args = parser.parse_args()

    # Gemini konfigurieren
    GeminiClient.initialize()

    for name, data in APPLICANTS.items():
        print(f"\n=== Bewerber: {name} ===\n")

        cover = TextProcessor.generate_anschreiben(
            job_text=JOB_DESCRIPTION,
            discipline=data["discipline"],
            previous_cover_letter=data["previous"],
            model=args.model
        )
        print("--- Generiertes Anschreiben (Markdown) ---\n")
        print(cover)

        score = TextProcessor.rate_job_match(
            job_description=JOB_DESCRIPTION,
            applicant_information=data["discipline"]
        )
        print(f"\n--- Job-Fit Score für {name}: {score} ---\n")


if __name__ == "__main__":
    main()