from projekt.backend.ai.gemini_client import GeminiClient
from projekt.backend.core.models import ApplicantProfile, JobDetails, AIModel


class TextProcessor:

    @staticmethod
    def generate_anschreiben(
            job_details: JobDetails,
            applicant_profile: ApplicantProfile,
            ai_model: AIModel = AIModel.FLASH
    ) -> str:
        """Generiert ein Anschreiben basierend auf JobDetails und ApplicantProfile."""
        prompt = f"""**Rolle:**
        Du bist ein erfahrener HR-Experte, spezialisiert auf das Verfassen überzeugender und professioneller Anschreiben. Du weißt genau, worauf Recruiter achten und wie man einen Bewerber optimal präsentiert. Deine Aufgabe ist es, basierend auf den bereitgestellten Informationen ein maßgeschneidertes Anschreiben für eine spezifische Stelle zu erstellen.

        **Eingabeinformationen (Input):**
        Du erhältst eine Sammlung von Informationen im Textformat, die Folgendes umfassen können:
        *   **Job-Informationen:** Details zur ausgeschriebenen Stelle (Aufgaben, Anforderungen, Unternehmen).
        *   **Bewerber-Profil:** Informationen über den Bewerber (relevante Auszüge aus dem Lebenslauf, Hard Skills, Soft Skills, Details zum Studium, persönliche Interessen, die relevant sein könnten).
        *   **Kontext/Bisheriges:** Gegebenenfalls Auszüge oder vollständige Versionen von bereits geschriebenen Anschreiben des Bewerbers als Referenz.

        **Wichtige Anweisungen und Einschränkungen (Constraints):**
        *   **Authentizität:** Das Anschreiben muss auf den tatsächlichen Fähigkeiten und Erfahrungen des Bewerbers basieren. Erfinde keine wesentlichen Qualifikationen oder Interessen hinzu. Die Aussagen müssen einer Überprüfung im Bewerbungsgespräch standhalten.
        *   **Positive, realistische Darstellung:** Hebe die Stärken des Bewerbers und die Passung zur Stelle überzeugend hervor. Stelle den Bewerber vorteilhaft dar, bleibe aber realistisch und vermeide Übertreibungen. Formuliere aktiv und selbstbewusst.
        *   **Relevanz:** Konzentriere dich auf die Informationen, die für die spezifische Stelle am relevantesten sind.
        *   **Keine Platzhalter:** Das Anschreiben sollte vollständig formuliert sein und keine offensichtlichen Platzhalter wie "[Hier Fähigkeit einfügen]" enthalten, es sei denn, eine Information fehlt explizit im Input.

        **Ausgabeformat (Output):**
        *   Generiere das vollständige Anschreiben im **Markdown-Format**.
        *   Strukturiere das Anschreiben klar und deutlich in die folgenden drei Abschnitte:
            *   **Einleitung:** Direkte Ansprache (falls Name bekannt, sonst allgemein), Bezug zur Stelle, Ausdruck des Interesses und kurze Vorstellung der Kernaussage/Motivation.
            *   **Hauptteil:** Ausführliche Darstellung der Motivation, Verknüpfung der relevantesten Fähigkeiten, Erfahrungen (aus Studium/Praxis) und Soft Skills mit den Anforderungen der Stelle. Begründung der Eignung.
            *   **Schluss:** Hinweis auf mögliche nächste Schritte (Einladung zum Gespräch), Gehaltsvorstellung/Eintrittsdatum (falls im Input gefordert/angegeben), Grußformel.

        Stellenbescheribung:
        {job_details.formatted_description or job_details.raw_text}

        Persoenliches Informationen:
        {applicant_profile.to_ai_prompt_format()}

        Vergangene Anschreiben:
        {applicant_profile.get_previous_cover_letters()}"""

        return GeminiClient.generate_content(
            prompt=prompt,
            model_type=ai_model.value,
            temperature=0.5
        )

    @staticmethod
    def rate_job_match(job_details: JobDetails, applicant_profile: ApplicantProfile) -> int:
        """Bewertet die Übereinstimmung zwischen Job und Bewerber (1-10)."""
        prompt = f"""**Rolle:**
        Du agierst als erfahrener Recruiting-Analyst oder Talent Assessment Spezialist. Deine Kernaufgabe ist die objektive Bewertung der **Gesamtübereinstimmung** (des "Fits"), wobei du das **Gesamtpaket** des Kandidaten betrachtest – einschließlich der Passung von Fähigkeiten, Erfahrungen **und explizit auch der Interessen** zu den Aufgaben und Anforderungen der Stelle. Du triffst keine Einstellungsentscheidung, sondern lieferst eine fundierte Einschätzung der Passung.

        **Eingabeinformationen (Input):**
        Du erhältst zwei klar getrennte Informationsblöcke im Textformat:
        1.  **Kandidatenprofil:** Enthält relevante Informationen über den Kandidaten (z.B. Auszüge aus dem Lebenslauf, Hard Skills, Soft Skills, Ausbildung/Studium, relevante Berufserfahrung, **genannte Interessen**).
        2.  **Stellenbeschreibung:** Enthält Details zur ausgeschriebenen Position (z.B. Aufgabenbereich, erforderliche Qualifikationen, gewünschte Fähigkeiten, Verantwortlichkeiten, Informationen zum Unternehmen/Team).

        **Wichtige Anweisungen und Einschränkungen (Constraints):**
        *   **Strikte Input-Basis:** Deine Bewertung und Analyse müssen *ausschließlich* auf den explizit bereitgestellten Informationen im Kandidatenprofil und der Stellenbeschreibung basieren. Interpretiere die Daten, aber füge keine externen Annahmen, nicht genannten Fähigkeiten oder Erfahrungen hinzu. Erfinde nichts.
        *   **Ganzheitlicher Abgleich:** Konzentriere dich auf den sachlichen Abgleich der Anforderungen der Stelle mit dem *gesamten* Profil des Kandidaten. Bewerte, wie gut das **Gesamtpaket** (Qualifikationen, Erfahrungen **und Interessen**) zur Stelle passt.
        *   **Interessen aktiv berücksichtigen:** Beziehe explizit mit ein, wie die genannten Interessen des Kandidaten potenziell zu den **Aufgaben**, dem Team oder der Unternehmenskultur (sofern beschrieben) passen könnten und ob sie die **Motivation oder Eignung** für die spezifischen Tätigkeiten positiv oder negativ beeinflussen.
        *   **Bewertungsskala (Intern):** Deine interne Bewertung soll auf einer Skala von 1 (Sehr geringe Übereinstimmung / Kaum relevante Qualifikationen/Passung im Gesamtpaket) bis 10 (Exzellente Übereinstimmung / Kandidat scheint ideal zu passen, auch hinsichtlich der Interessen) erfolgen. Berücksichtige dabei alle Aspekte des Profils im Verhältnis zur Stelle.

        **Ausgabeformat (Output):**
        *   Gib **ausschließlich** eine einzelne Ganzzahl (Integer) zwischen 1 und 10 als finale Bewertung der Gesamtpassung aus.
        *   **Keine** weiteren Texte, Erklärungen, Formatierungen oder einleitende Sätze. Nur die Zahl.

        # --- HIER BEGINNEN DIE DATEN ---

        **Kandidatenprofil:**
        {applicant_profile.to_ai_prompt_format()}

        **Stellenbeschreibung:**
        {job_details.formatted_description or job_details.raw_text}
        """

        result = GeminiClient.generate_content(
            prompt=prompt,
            model_type=AIModel.FLASH_2.value,
            temperature=0.05  # Niedrige Temperatur für konsistentere Bewertungen
        )

        try:
            return int(result.strip())
        except (ValueError, TypeError):
            print(f"Konnte Rating nicht parsen: {result}")
            return 0

    @staticmethod
    def format_job_description(html_code: str) -> str:
        """Formatiert Jobbeschreibungen in strukturiertes Markdown."""
        prompt = f"""Aufgabe: Extrahiere spezifische Informationen aus dem folgenden Text einer Jobbeschreibung und formatiere sie als klar strukturierte Markdown-Datei, die den Inhalt des Originals präzise widerspiegelt.
        WICHTIG:
        1.  **Inhalts-Extraktion & Zuordnung:** Extrahiere **ausschließlich** Informationen, die zu den folgenden Themenblöcken gehören, falls sie im Originaltext vorhanden sind. Ordne den extrahierten Text **genau** diesen Themen und der vorgegebenen Reihenfolge zu:
            *   **Jobbezeichnung:** einfach frei lassen.
            *   **Unternehmen Infos:** Eine kurze Beschreibung des Unternehmens und/oder der Rolle im Unternehmen.
            *   **Deine Aufgaben:** Eine detaillierte Liste oder Beschreibung der Tätigkeiten und Verantwortlichkeiten.
            *   **Dein Profil:** Die erforderlichen oder gewünschten Qualifikationen, Fähigkeiten und Erfahrungen des Bewerbers (fachliche Anforderungen).
            *   **Benefits:** Angebotene Vorteile, Zusatzleistungen oder Vergünstigungen.
            *   **Standort:** Der Arbeitsort oder die relevanten Standortinformationen.
            *   **(Alle anderen Textteile des Originals sind strikt zu ignorieren und dürfen NICHT im Output erscheinen.)**

        2.  **Text-Treue und minimale Anpassung:** Der Kerninhalt und die Bedeutung der extrahierten Blöcke müssen dem Original entsprechen.
            *   **Behalte den originalen Wortlaut so weit wie möglich bei.** Der Output soll klar zeigen, was im Original stand.
            *   Du darfst **nur minimale Anpassungen** zur Verbesserung der Lesbarkeit vornehmen (z. B. offensichtliche Tippfehler korrigieren, uneinheitliche Aufzählungszeichen in Markdown-Listen vereinheitlichen).
            *   **Füge keine neuen Informationen hinzu**, interpretiere nicht über den Text hinaus und ändere nicht den Sinn oder den Tonfall des Originaltextes.

        3.  **Markdown-Formatierung:**
            *   Strukturiere den extrahierten Inhalt mithilfe von Markdown.
            *   Verwende **genau die folgenden Markdown-Überschriften (Level 2 `##`)** für die entsprechenden extrahierten Inhaltsblöcke, sofern Inhalt dafür gefunden wurde:
                *   `## Jobbezeichnung` (frei lassen)
                *   `## Unternehmen Infos` (für die Unternehmens-/Rollenbeschreibung)
                *   `## Deine Aufgaben` (für die Aufgabenliste)
                *   `## Dein Profil` (für die Qualifikationen)
                *   `## Benefits` (für die Zusatzleistungen)
                *   `## Standort` (für den Arbeitsort)
            *   **Wichtig:** Der unter einer Überschrift formatierte Text muss **exakt** dem Inhalt entsprechen, der im Originaldokument für diesen Themenbereich (z.B. alle gefundenen Aufgaben unter `## Deine Aufgaben`, alle Qualifikationen unter `## Dein Profil`) identifiziert wurde.
            *   Wandle passende Textabschnitte (insbesondere Aufgaben, Profilpunkte, Benefits) in Markdown-Listen (`-` oder `*`) um. Achte auf Konsistenz innerhalb einer Liste.
            *   Nutze Absätze und Zeilenumbrüche sinnvoll zur Verbesserung der Lesbarkeit.

        4.  **Input-Verarbeitung:** Falls der Text HTML-Code enthält, extrahiere zuerst den reinen Textinhalt, bevor du mit der Zuordnung und Formatierung beginnst. Ignoriere dabei alle HTML-Tags.

        Ziel: Der Output soll eine präzise strukturierte Jobbeschreibung im Markdown-Format sein. Sie soll **ausschließlich** die oben definierten relevanten Inhalte unter den **vorgegebenen Überschriften** enthalten, sodass klar ersichtlich ist, welche Informationen zu welchem Thema im Originaltext standen. Das Ergebnis muss valides Markdown sein und eine hohe Texttreue zum Original aufweisen.

        Hier ist der zu verarbeitende Text:

        {html_code}

        Stelle sicher, dass der Output nur die extrahierten und formatierten relevanten Blöcke unter den korrekten Überschriften enthält und sonst nichts.
        """

        return GeminiClient.generate_content(
            prompt=prompt,
            model_type=AIModel.FLASH_2.value,
            temperature=0.2
        )