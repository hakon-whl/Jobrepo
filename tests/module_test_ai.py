import os
import sys

# Damit "import projekt.backend..." funktioniert:
TEST_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from projekt.backend.core.config import app_config
app_config.ai.gemini_api_key = "AIzaSyB880bqvOVEs-uBpdukKPIaRYGMfvSUvdo"


from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.core.models import ApplicantProfile, JobDetails, JobSource

JOB_DESCRIPTION = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Praktikant Softwaretests & Business Analyse (m/w/d) bei Allianz</title>
    <style>
        body {
            font-family: sans-serif;
            line-height: 1.6;
            margin: 20px;
        }
        h1, h2, h3 {
            color: #333;
        }
        ul {
            margin-bottom: 15px;
        }
        li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>

    <h1>Praktikant im Bereich Softwaretests & Business Analyse (m/w/d)</h1>
    <h2>Willkommen bei der Allianz</h2>

    <p>
        Data Analytics und Künstliche Intelligenz beschleunigen weiter stark den
        technologischen Wandel in allen Unternehmensbereichen der Versicherungen.
        Die Allianz in Deutschland baut deshalb neue Expertise, Prozesse und
        Infrastruktur auf, um das Potential von Data Analytics nutzbar zu machen.
        Bei uns arbeitest Du im Herzen eines der wichtigsten Zukunftsfelder
        unserer Branche.
    </p>

    <p>
        Wir betreuen, verantworten und gestalten ganzheitlich die Strategie,
        Prozesse und Infrastruktur im Bereich Data Analytics, sowohl für Business
        Intelligence als auch „Big Data" Anwendungen. Wir erarbeiten gemeinsam
        mit verschiedenen Stakeholdern aus den Geschäftsbereichen die Data
        Analytics Strategie und Projekt-Roadmap und verantworten den Aufbau einer
        modernen Infrastruktur.
    </p>

    <p>
        Wir suchen zum nächstmöglichen Zeitpunkt Unterstützung für den Bereich
        Testing, Qualitätssicherung und Business Analyse im Umfeld Business
        Intelligence und Data Analytics.
    </p>

    <h2>Deine Aufgaben</h2>
    <p>Das erwartet dich bei uns als Praktikant im Bereich Softwaretests &
    Business Analyse (m/w/d):</p>
    <ul>
        <li>Du arbeitest an einem strategischen, konzernübergreifenden Vorhaben
            in einem cross-funktionalen Team mit agilen
            Projektmanagementmethoden.</li>
        <li>Dabei übernimmst Du schrittweise eigene Aufgabenpakete im Umfeld
            Softwaretests und Qualitätssicherung sowie Business Analyse im
            Umfeld Business Intelligence und Data Analytics.</li>
        <li>Du unterstützt das Team in der Datenanalyse und kannst auch eigene
            Datenauswertungen erstellen.</li>
        <li>Du lernst Technologien für Analytics-Anwendungen kennen.</li>
        <li>Du arbeitest mit spannenden Technologien (z. B. Oracle Cloud
            Infrastructure, DB2, SAS Enterprise Guide, SQL, Jira,
            Confluence).</li>
    </ul>

    <h2>Dein Profil</h2>
    <ul>
        <li>Du bist auf der Suche nach einem Pflichtpraktikum im Rahmen deines
            Studiums der (Wirtschafts-)Informatik oder einem ähnlichen
            Studiengang.</li>
        <li>Du verfügst über Kenntnisse im Umgang mit diesen Technologien:
            Relationale Datenbanken (v. a. Oracle Cloud Infrastructure, DB2),
            SAS (SAS Base, Enterprise Guide), SQL.</li>
        <li>Idealerweise konntest du schon erste Erfahrungen im Bereich
            Softwaretests und Qualitätssicherung sowie mit DWH/BI-Architekturen
            sammeln.</li>
        <li>Wünschenswert sind Erfahrungen mit und Wissen zu Methoden im Bereich
            des agilen Projektmanagements (z. B. Scrum).</li>
        <li>Du hast verhandlungssichere Deutsch- und gute Englischkenntnisse.</li>
    </ul>

</body>
</html>
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

def main():
    tp = TextProcessor()

    # 1) Job-Beschreibung formatieren
    print("\n=== Formatted Job Description ===\n")
    formatted = tp.format_job_description(JOB_DESCRIPTION)
    print(formatted[:500] + "\n…\n")

    # JobDetails mit formatiertem Text
    job = JobDetails(
        title="Praktikant Softwaretests & Business Analyse",
        title_clean="Praktikant Softwaretests & Business Analyse",
        raw_text=JOB_DESCRIPTION,
        formatted_description=formatted,
        url="https://example.com/job",
        source_site=JobSource.STEPSTONE
    )

    # 2) Für jeden Bewerber: Rating und Anschreiben
    for name, data in APPLICANTS.items():
        profile = data["profile"]
        print(f"\n--- Ergebnisse für {name} ---")

        rating = tp.rate_job_match(job, profile)
        print(f"Job-Match Rating: {rating}/10")

        cover_letter = tp.generate_anschreiben(job, profile)
        snippet = cover_letter[:300].replace("\n", " ")
        print(f"\nAnschreiben (erste 300 Zeichen):\n{snippet}…\n")

if __name__ == "__main__":
    main()