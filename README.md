 # Job-Scraping & KI-Bewerbungsassistent 🤖💼

Ein intelligentes Full-Stack-System zum automatischen Suchen, Bewerten und Bewerben auf Jobs mit KI-Unterstützung.

## 🌟 Features

### 🔍 **Multi-Platform Job-Scraping**
- **StepStone**, **Xing** und **Stellenanzeigen.de** Integration

### 🤖 **KI-gestützte Analyse**
- **Automatische Job-Bewertung** (1-10 Skala) basierend auf Profil-Matching
- **Personalisierte Anschreiben-Generierung** mit Google Gemini AI
- **Intelligente Job-Beschreibung-Formatierung**
- Konfigurierbare AI-Modelle und Parameter

### 📄 **PDF-Management**
- **Automatische PDF-Erstellung** für alle gefundenen Jobs
- **Zusammengefasste PDF-Ausgabe** sortiert nach Bewertung

## 🏗️ Technologie-Stack

### Backend
- **Python 3.9+** mit Flask
- **Selenium** + **BeautifulSoup** für Web-Scraping
- **Requests** + **BeautifulSoup**für HTTP-Client
- **Google Gemini API** für KI-Features
- **PyPDF2** + **xhtml2pdf** für PDF-Verarbeitun

### Frontend
- **React 19**


## 📁 Projektstruktur

```
infosys_done/
├── projekt/
│   ├── backend/
│   │   ├── ai/                  
│   │   │   ├── prompts/          
│   │   │   ├── gemini_client.py  
│   │   │   ├── text_processor.py 
│   │   │   └── prompt_manager.py 
│   │   ├── core/                 
│   │   │   ├── models.py         
│   │   │   ├── config.py        
│   │   │   └── main.py          
│   │   ├── scrapers/            
│   │   │   ├── stepstone_scraper.py
│   │   │   ├── xing_scraper.py
│   │   │   └── stellenanzeigen_scraper.py
│   │   └── utils/                
│   │       ├── pdf_utils.py      
│   │       └── html_parser.py   
│   └── frontend/
│       ├── src/
│       │   ├── components/     
│       │   ├── services/        
│       │   ├── hooks/         
│       │   └── constants/       
│       └── public/
├── main.py                      
└── requirements.txt
```

## 🚀 Installation & Setup

### 1. Repository klonen
```bash
git clone <repository-url>
cd infosys_done
```

### 2. Python Dependencies installieren
```bash
pip install -r requirements.txt
```

### 3. Frontend Dependencies installieren
```bash
cd projekt/frontend
npm install
npm run build
cd ../..
```

### 4. Umgebungsvariablen konfigurieren
Erstelle eine `.env` Datei im Projektroot:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
```

### 5. Chrome WebDriver installieren
Der ChromeDriver wird automatisch über `webdriver-manager` installiert.

## ⚙️ Konfiguration

### AI-Modelle konfigurieren
In `projekt/backend/core/config.py`:

```python
@dataclass
class AIConfig:
    # Anschreiben-Generierung
    cover_letter_model: AIModel = AIModel.FLASH
    cover_letter_temperature: float = 0.5
    
    # Job-Rating
    rating_model: AIModel = AIModel.FLASH_2
    rating_temperature: float = 0.05
    
    # Job-Formatierung
    formatting_model: AIModel = AIModel.FLASH_2
    formatting_temperature: float = 0.2
```

### Scraping-Parameter anpassen
```python
@dataclass
class ScrapingConfig:
    max_pages_per_site: int = 6
    max_jobs_per_session: int = 20
    default_request_delay: tuple = (2.0, 5.0)
    max_retries: int = 3
```

## 🎯 Verwendung

### 1. Server starten
```bash
python module_test.py
```

### 2. Web-Interface öffnen
Navigiere zu `http://localhost:5000`

### 3. Bewerbungsprofil erstellen
- **Jobtitel** und **Ort** eingeben
- **Studium** und **Interessen** beschreiben
- **Skills** auswählen oder hinzufügen
- **CV/Anschreiben PDFs** hochladen (optional)

### 4. Job-Suche starten
- **Jobseite** auswählen (StepStone/Xing/Stellenanzeigen.de)
- **Radius** und **Disziplin** einstellen
- Suche starten und **automatisch generierte PDF** herunterladen

## 📊 AI-Rating System

Das System bewertet Jobs auf einer **1-10 Skala** basierend auf:

- ✅ **Skill-Match** (Technische Fähigkeiten)
- ✅ **Studium-Relevanz** (Fachlicher Hintergrund)
- ✅ **Interessen-Passung** (Persönliche Motivation)
- ✅ **Aufgaben-Kompatibilität** (Job-Anforderungen)

**Jobs mit Rating ≥ 5** erhalten automatisch generierte Anschreiben.

## 🛠️ Entwicklung

### Backend erweitern
Neue Scraper hinzufügen:
```python
# projekt/backend/scrapers/new_site_scraper.py
class NewSiteScraper(RequestBaseScraper):
    def __init__(self):
        super().__init__("NewSite")
    
    def get_search_result_urls(self, search_criteria):
        # Implementation
        pass
```

### Frontend-Komponenten
```jsx
// projekt/frontend/src/components/NewComponent.js
import React from 'react';

const NewComponent = ({ props }) => {
    return <div>Component Content</div>;
};

export default NewComponent;
```

## 🚨 Troubleshooting

### Häufige Probleme

**1. Gemini API Fehler**
```bash
Fehler: Gemini API-Schlüssel ist erforderlich
```
→ Prüfe `.env` Datei und `GEMINI_API_KEY`

**2. ChromeDriver Probleme**
```bash
WebDriver Fehler: Chrome binary not found
```
→ Installiere Chrome Browser oder update ChromeDriver

**3. PDF-Erstellung fehlgeschlagen**
```bash
PDF-Erstellung Fehler: wkhtmltopdf not found
```
→ Alternative: `xhtml2pdf` wird automatisch verwendet

**4. Frontend Build-Fehler**
```bash
Module not found: pdfjs-dist
```
→ Führe `npm run copy-pdf-worker` aus

## 📈 Performance-Optimierung

### Scraping-Performance
- **Request-Delays** zwischen 2-5 Sekunden
- **Retry-Mechanismus** mit exponential backoff
- **Session-Management** für Selenium

### AI-Optimierung
- **Model-Caching** für wiederholte Anfragen
- **Batch-Processing** für mehrere Jobs
- **Temperature-Tuning** für konsistente Ergebnisse

## 🤝 Contributing

1. **Fork** das Repository
2. **Feature Branch** erstellen (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Pull Request** öffnen

## 📄 Lizenz

Dieses Projekt ist unter der **MIT License** lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

## 👤 Autor

**Hakon**
- Student der Wirtschaftsinformatik - Informationstechnologie an der HM München
- GitHub: [@hakon-username](https://github.com/hakon-username)

## 🙏 Danksagungen

- **Google Gemini API** für KI-Funktionalitäten
- **Selenium** Team für Web-Automation
- **React** Community für Frontend-Framework
- **StepStone**, **Xing**, **Stellenanzeigen.de** für Jobdaten

---

⭐ **Star** dieses Repository wenn es dir hilft! ⭐