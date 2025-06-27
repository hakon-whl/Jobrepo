# Job-Scraping & KI-Bewerbungsassistent 🤖💼

Eine Web-Anwendung, die automatisch Praktikumsstellen auf StepStone und Xing durchsucht, KI-gestütztes Matching durchführt, 
individuelle Anschreiben generiert und alle Ergebnisse als sortierte PDF-Zusammenfassung ausliefert.

---

## 🌟 Features

- **Multi-Platform Scraping**  
  – StepStone & Xing  
- **KI-gestützte Analyse**  
  – Job-Match-Rating (Skala 1–10)  
  – Personalisiertes Anschreiben mit Google Gemini  
  – Formatierung unstrukturierter Job-Beschreibungen  
- **PDF-Management**  
  – Pro Stelle automatisch generierte PDF  
  – Zusammenführung und Sortierung nach Rating  
- **Profileingabe im Frontend**  
  – Jobkriterien, Studium, Interessen, Skills  
  – PDF Upload & Text-Extraktion im Client
- **Custom-Skills**  
  – Vordefinierte Basis-Skills plus eigene Skills  
  – Persistenz durch speicherung im LocalStorage  

---

## 🏗️ Technologie-Stack

**Backend (Python 3.9+)**  
- Flask (Bereitstellung der REST-API-Endpoints & Auslieferung des statischen Frontend-Builds)
- Requests + BeautifulSoup (Versenden von HTTP-Anfragen)
- Selenium + webdriver-manager (Headless-Browser-Automatisierung für dynamische / Lazy-Load-Seiten)  
- BeautifulSoup (Parsen von HTML für das Web-Scraping)
- google-generativeai (Client-Bibliothek zur Anbindung an Google Gemini AI-Modelle für Text-Generierung)  
- xhtml2pdf & PyPDF2 (Konvertierung von HTML/Markdown in PDF & Zusammenführen mehrerer PDF-Dateie)  

**Frontend (React 18+)**  
- React, React-DOM, React-Hook-Form (Erstellen der UI-Komponenten, DOM-Rendering & Formular-Validierung)
- PDF.js (Parsen und Extrahieren von Text aus hochgeladenen PDF-Dokumenten im Browser)
- LocalStorage (Persistenz und Verwaltung der benutzerdefinierten Skills im Client)

---

## 📁 Projektstruktur

```plaintext
infosys_done/
└── projekt/
    ├── backend/
    │   ├── ai/
    │   │   ├── prompts/
    │   │   │   ├── cover_letter_generation.txt
    │   │   │   ├── job_description_formatting.txt
    │   │   │   └── job_rating.txt
    │   │   ├── gemini_client.py
    │   │   ├── prompt_manager.py
    │   │   └── text_processor.py
    │   ├── core/
    │   │   ├── api_key.txt
    │   │   ├── config.py
    │   │   └── models.py
    │   ├── scrapers/
    │   │   ├── request_base_scraper.py
    │   │   ├── selenium_base_scraper.py
    │   │   ├── stepstone_scraper.py
    │   │   └── xing_scraper.py
    │   ├── temp_pdfs/
    │   └── utils/
    │       ├── html_parser.py
    │       └── pdf_utils.py
    ├── frontend/
    │   ├── build/
    │   ├── node_modules/
    │   ├── public/
    │   └── src/
    │       ├── components/
    │       ├── constants/
    │       ├── hooks/
    │       └── services/
    ├── main.py
    └── requirements.txt
└── tests/
```

---

## 🚀 Motivation

Aktuell verbringen Studierende, wie meine Kommilitonen, viel Zeit mit der Suche nach einer passenden Praxissemesterstelle. Diese zeitaufwändige Suche, kombiniert mit dem Aufwand für individuelle Bewerbungen neben dem Studium und möglichen Minijobs oder Werkstudententätigkeiten, gestaltet sich nahezu unmöglich.

Mein Tool automatisiert:

1. Relevante Angebote identifizieren: Aktuell fokussiert auf Praktika und Werkstudentenjobs.
2. Profil-Matching: Abgleich zwischen Stellenbeschreibungen und Bewerberprofilen, um die wichtigsten Übereinstimmungen herauszuarbeiten.
3. Erstellung individueller Anschreiben: Generierung passgenauer Anschreiben auf Basis von vorliegenden Informationen, wobei spezifische Details zu früheren Anstellungen oder Fähigkeiten aus den PDfs integriert werden.
4. Zusammenfassung der Ergebnisse: Aufbereitung aller relevanten Informationen in einer PDF-Zusammenfassung. Hierbei werden die Ergebnisse für jeden Job, der einen Mindestschwellenwert erreicht hat, einzeln dargestellt und anschließend in einer finalen PDF-Ausgabe für das Frontend zusammengefasst.  

Durch diese Automatisierung bleibt mehr Zeit für fachliche Inhalte und die persönliche Vorbereitung.

---

## ⚠️ Probleme & Lösungsansatz

- **Dynamische Seiten und Lazy-Loading (Xing)**  
    Anfänglich traten Probleme bei der Extraktion aller relevanten Informationen von der Xing-Webseite auf. Im Gegensatz zu StepStone basiert Xing auf JavaScript. Dies erschwert die Informationsverarbeitung durch Lazy-Loading und dient zudem als Mechanismus gegen Web-Scraping. Daher war es notwendig, eine geeignete Lösung für diese Herausforderung zu entwickeln.
    <br>
    → Einsatz von Headless-Selenium zur serverseitigen Wiedergabe mit kontrollierten Scroll-Schleifen (bei 25 Anzeigen pro Lazy-Load-Schritt: Anzahl der Anzeigen / 25 = benötigte Scroll-Vorgänge).

---

## 🔄 Ablauf (End-to-End)

1. **Formular-Eingabe (Frontend)**  
   – Erfassung von Jobkriterien, Studieninformationen, Interessen, Fähigkeiten sowie hochgeladenen PDF-Dokumenten.
2. **PDF-Text-Extraktion**  
   – Durchführung der Text-Extraktion aus PDF-Dokumenten im Client mittels PDF.js.
3. **API-Request**  
   – Versand der gesammelten Daten über einen POST-Request an /api/create_job.
4. **Session-Verzeichnis**  
   – Anlegen eines temporären Verzeichnisses, das zeit- und parameterbasiert benannt ist, zur Speicherung von PDF-Dateien während der Sitzung.
5. **Scraping**  
   - **StepStone**  
     • HTTP-Client mit Requests → HTML abrufen → Ermittlung der Gesamtzahl der Anzeigen → Extraktion der relevanten Stellen-Links → Parsing der Detailinformationen zu jeder Stelle
   - **Xing**  
     • Headless-Chrome via Selenium → Seite laden → Ermittlung der erforderlichen Anzahl von Scroll-Vorgängen → Durchführung von "Scroll-to-Bottom"-Aktionen → Extraktion der relevanten Stellen-Links → Parsing der Detailinformationen zu jeder Stelle
6. **KI-Pipeline**  
   – Jede Stelle: nach  Praktikum/Werkstudenten gefiltert (Schlüsselbegriffe) → Job-Beschreibung formatieren → Rating abfragen → Anschreiben generieren, wenn das Rating (rating ≥ cover_letter_min_rating_premium oder rating ≥ cover_letter_min_rating)
7. **PDF-Erzeugung & Merge**  
   – Markdown-Teile (Rating, Titel, Beschreibung, Anschreiben) → xhtml2pdf → einzelne PDFs →  
     sortieren nach Rating → Zusammenführen mit PyPDF2 → `summary.pdf`.  
8. **Download**  
   – `summary.pdf` als Antwort an den Client.

---
## 🔮 Verbesserungen & Ausblick

- **Parallelisierung des Scrapings**  
  • Einsatz von `asyncio` + `aiohttp` (oder alternativ Python-`multiprocessing`), um
    -  die Extraktion der Job-URLs gleichzeitig zu bearbeiten
  → Verkürzt die Wartezeiten und nutzt Systemressourcen effizienter.

- **Multithreading für KI-Anfragen**  
  • Das Rating und die Anschreiben-Generierung via Google Gemini API dominieren die Laufzeit.  
  • Durch einen Thread-Pool können mehrere Anfragen parallel abgewickelt werden
  → Reduziert insgesamt die Antwortzeiten drastisch

- **Manuelle Nachbearbeitung im Frontend**  
  • Nach dem KI-Entwurf wird ein eingebetteter Editor (Markdown oder Rich-Text) bereitgestellt 
  • Nutzer können den Anschreiben-Text selbst anpassen, Layout ändern oder Abschnitte ergänzen
  → Mehr Kontrolle und Individualisierung vor dem PDF-Export

- **Persistente Ergebnis-Speicherung**  
  • Statt nur temporärer Dateien im `temp_pdfs`-Verzeichnis:  
    - Speichern aller generierten PDFs, Ratings, verwendeter Modelle und Prompts  
    - in einer Datenbank (z. B. PostgreSQL oder MongoDB)
  • Ermöglicht Analytics und kontinuierliches Prompt-Tuning auf Basis realer Nutzerdaten

Durch diese Erweiterungen wird das System
- spürbar schneller in der Verarbeitung  
- und bietet den Anwendern mehr Interaktivität sowie eine lernende Grundlage zur weiteren Verbesserung der Anschreiben-Qualität

---
## ⚙️ Installation

### 1. Repository klonen  
```bash
git clone <URL>
cd infosys_done/projekt
```

### 2. Backend einrichten  
```bash
pip install -r requirements.txt
```

### 3. Frontend einrichten  
```bash
cd frontend
npm install
npm run build
```

---

## 🔧 Konfiguration

1. **API-Key**  
   – Datei `backend/core/api_key.txt` mit Ihrem Google Gemini-API-Schlüssel füllen.  

2. **Pfade**  
   – In `backend/core/config.py` unter `PathConfig` Pfade zu Frontend-Build, Temp-PDFs, Prompts, Logs anpassen.  

3. **AI-Modelle & Parameter**  
   – In `backend/core/config.py` unter `AIConfig` Modelle (`AIModel`-Enum) und Temperaturen einstellen.  

4. **Scraping-Parameter**  
   – In `backend/core/config.py` unter `ScrapingConfig` Delays, Timeouts, Retry-Strategien, Selenium-Defaults justieren.

5. **Filter von Jobs durch Jobkeys (Praktikum, Werkstudent, ...) erweitern**  
   – In `backend/core/models.py` unter `JobDetailsScraped` in der `__post_init__(self)` Methode.
6. **Config Allgemein**
   - In der Datei backend/core/config.py sind sämtliche globalen Parameter definiert. Dies umfasst beispielsweise die Anzahl der Jobs in der Zusammenfassung (summary) sowie die CSS-Selektoren für das HTML-Parsing. Falls Anpassungswünsche bestehen, bietet die Datei backend/core/config.py üblicherweise alle notwendigen Elemente für eine Individualisierung.

---

## ▶️ Verwendung

```bash
 cd projekt
python -m projekt.main
```

1. Browser öffnen: `http://localhost:5000`  
2. Formular ausfüllen (Jobsuche, Profil, PDF-Upload).  
3. Auf **„Bewerbung senden“** klicken.  
4. Automatisch generierte und zusammengeführte `summary.pdf` herunterladen.

---

## 👤 Über mich
Ich bin nach der Abgabe des Projekts hochmotiviert, weiter daran zu arbeiten, wie man am Umfang des Projekts erkennen kann. Lustigerweise habe ich meinen Praxissemesterjob mit meinem Prototypen gefunden. Haben Sie Tipps, wie ich meine Anwendung erfolgreich 'an den Markt bringen' – besser gesagt, den Leuten zur Verfügung stellen – kann, ohne potenzielle Probleme mit den jeweiligen Jobseiten zu bekommen? Dabei sind mir Dinge wie GitHub und Subreddits bereits ein Begriff. Mit freundlichen Grüßen
**Hakon Wahl**  
- Student der Wirtschaftsinformatik – Informationstechnologie, HM München  
- GitHub: [@hakon-username](https://github.com/hakon-username)  
- E-Mail: hakon.wahl@gmail.com  

---

*Viel Erfolg beim Ausprobieren!*