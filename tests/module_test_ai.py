
from projekt.backend.ai.text_processor import TextProcessor
from projekt.backend.core.config import app_config
from projekt.backend.core.models import (
    ApplicantProfile,
    JobDetailsScraped,
    JobSource,
    AIModel
)

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

# Korrekte Struktur für Test-Applicants
APPLICANTS = {
    "Alice": ApplicantProfile(
        study_info="Wirtschaftsinformatik an der HM München, 5. Semester",
        interests="Softwaretesting, Datenanalyse, agile Methoden",
        skills=["Python", "SQL", "Git", "Scrum", "Test-Automation"]
    ),
    "Bob": ApplicantProfile(
        study_info="Betriebswirtschaftslehre an der LMU München, 4. Semester",
        interests="Projektmanagement, Stakeholder-Management, Prozessoptimierung",
        skills=["Excel", "PowerPoint", "Kommunikation", "Teamarbeit"]
    )
}


def main():
    tp = TextProcessor()

    formatted = tp.format_job_description(JOB_DESCRIPTION)
    print("Formatiert:", formatted[:200])

    job = JobDetailsScraped(
        title="Praktikant Softwaretests & Business Analyse",
        raw_text=JOB_DESCRIPTION,
        url="https://example.com/job",
        source=JobSource.STEPSTONE
    )

    for name, profile in APPLICANTS.items():
        print(f"\n--- {name} ---")

        rating = tp.rate_job_match(job, profile)
        print(f"Rating: {rating}/10")
        if rating >= app_config.ai.cover_letter_min_rating_premium:
            cover_letter = tp.generate_anschreiben(job, profile, app_config.ai.cover_letter_model_premium.value)
            print(app_config.ai.cover_letter_model_premium.value)
            snippet = cover_letter[:300].replace("\n", " ")
            print(f"Anschreiben: {snippet}...")
        elif rating >= app_config.ai.cover_letter_min_rating:
            cover_letter = tp.generate_anschreiben(job, profile, app_config.ai.cover_letter_model.value)
            snippet = cover_letter[:300].replace("\n", " ")
            print(app_config.ai.cover_letter_model.value)
            print(f"Anschreiben: {snippet}...")


if __name__ == "__main__":
    main()