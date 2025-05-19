import os
from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.ai.text_processor import TextProcessor


def main():
    # Stelle sicher, dass die API konfiguriert ist
    GeminiClient.initialize()

    print("===== TextProcessor Funktionalitätstest =====\n")

    # 1. Test: Jobbeschreibung formatieren
    print("1. Test: Jobbeschreibung formatieren")
    html_job_beschreibung = """
    <div class="job-description">
        <h2>Junior Software Developer (m/w/d)</h2>
        <div class="company-info">
            <p>Bei XYZ Tech entwickeln wir innovative Lösungen für die Zukunft. Unser Team besteht aus kreativen Köpfen, die jeden Tag neue Herausforderungen meistern.</p>
        </div>
        <div class="responsibilities">
            <h3>Deine Aufgaben:</h3>
            <ul>
                <li>Entwicklung von Softwarelösungen in Python und JavaScript</li>
                <li>Mitarbeit an agilen Projekten</li>
                <li>Code-Reviews durchführen</li>
                <li>Teilnahme an Sprint-Meetings</li>
            </ul>
        </div>
        <div class="requirements">
            <h3>Dein Profil:</h3>
            <ul>
                <li>Abgeschlossenes Studium der Informatik oder vergleichbare Qualifikation</li>
                <li>Erste Erfahrung mit Python und JavaScript</li>
                <li>Grundkenntnisse in Git und SQL</li>
                <li>Teamfähigkeit und Kommunikationsstärke</li>
            </ul>
        </div>
        <div class="benefits">
            <h3>Wir bieten:</h3>
            <ul>
                <li>Flexible Arbeitszeiten</li>
                <li>Homeoffice-Möglichkeiten</li>
                <li>Weiterbildungsmöglichkeiten</li>
                <li>Moderner Arbeitsplatz im Herzen von Berlin</li>
            </ul>
        </div>
        <div class="location">
            <p>Standort: Berlin, Deutschland</p>
        </div>
    </div>
    """
    try:
        formatted_job = TextProcessor.format_job_description(html_job_beschreibung)
        print("\nFormatierte Jobbeschreibung:")
        print(formatted_job)
        print("\n" + "-" * 50 + "\n")
    except Exception as e:
        print(f"Fehler bei der Formatierung der Jobbeschreibung: {e}")

    # 2. Test: Bewerbung und Job-Match bewerten
    print("2. Test: Bewerbung und Job-Match bewerten")
    job_description = """
    ## Deine Aufgaben
    - Entwicklung von Softwarelösungen in Python und JavaScript
    - Mitarbeit an agilen Projekten
    - Code-Reviews durchführen
    - Teilnahme an Sprint-Meetings

    ## Dein Profil
    - Abgeschlossenes Studium der Informatik oder vergleichbare Qualifikation
    - Erste Erfahrung mit Python und JavaScript
    - Grundkenntnisse in Git und SQL
    - Teamfähigkeit und Kommunikationsstärke
    """

    applicant_information = """
    Studium: Informatik (Bachelor), TU Dresden, Abschluss 2023
    Programmiererfahrung: Python (2 Jahre), JavaScript (1 Jahr), HTML/CSS
    Berufserfahrung: 6-monatiges Praktikum bei einer Webentwicklungsfirma
    Soft Skills: Teamorientiert, lernbereit, kommunikativ
    Interessen: Webentwicklung, Open-Source-Projekte, KI
    """

    try:
        match_score = TextProcessor.rate_job_match(job_description, applicant_information)
        print(f"\nJob-Match Bewertung (1-10): {match_score}")
        print("\n" + "-" * 50 + "\n")
    except Exception as e:
        print(f"Fehler bei der Job-Match Bewertung: {e}")

    # 3. Test: Anschreiben generieren
    print("3. Test: Anschreiben generieren")
    job_text = """
    Junior Python Developer (m/w/d)

    Wir suchen einen motivierten Junior Entwickler mit Python-Kenntnissen für unser wachsendes Team.

    Aufgaben:
    - Entwicklung von Backend-Komponenten mit Python
    - Mitarbeit an der Weiterentwicklung unserer Plattform
    - Zusammenarbeit mit dem Frontend-Team
    - Testen und Dokumentieren von Code

    Anforderungen:
    - Grundkenntnisse in Python
    - Interesse an agilen Entwicklungsmethoden
    - Teamfähigkeit und Kommunikationsstärke
    - Erste Erfahrungen mit Datenbanken von Vorteil
    """

    discipline = """
    Informatik-Bachelor mit Schwerpunkt Softwareentwicklung.
    Python-Kenntnisse durch Studienprojekte und ein 6-monatiges Praktikum.
    Grundkenntnisse in SQL, Git und agilen Methoden.
    """

    previous_letter = """
    Sehr geehrte Damen und Herren,

    mit großem Interesse habe ich Ihre Stellenanzeige als Frontend-Entwickler entdeckt und bewerbe mich hiermit um diese Position.

    Während meines Informatik-Studiums habe ich verschiedene Webprojekte umgesetzt und konnte dabei meine Fähigkeiten in HTML, CSS und JavaScript vertiefen. Besonders das Arbeiten mit React hat mir viel Freude bereitet.

    Ich freue mich über die Möglichkeit, in einem persönlichen Gespräch mehr über die Position zu erfahren.

    Mit freundlichen Grüßen
    """

    try:
        anschreiben = TextProcessor.generate_anschreiben(job_text, discipline, previous_letter)
        print("\nGeneriertes Anschreiben:")
        print(anschreiben)
    except Exception as e:
        print(f"Fehler bei der Generierung des Anschreibens: {e}")


if __name__ == "__main__":
    main()
