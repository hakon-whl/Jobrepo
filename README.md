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

### Datenpfad anpassen
```python
@dataclass
class PathConfig:
    frontend_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\frontend"
    temp_pdfs_dir: str = r"C:\Users\wahlh\PycharmProjects\Jobrepo\projekt\backend\temp_pdfs"
    prompts_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\ai\prompts"
    logs_dir: str = r"C:\Users\wahlh\PycharmProjects\infosys_done\projekt\backend\logs"
```


### Scraping-Parameter anpassen
```python
@dataclass
class ScrapingConfig:
    max_pages_per_site: int = 6
    max_jobs_per_session: int = 20
    default_request_delay: tuple = (2.0, 5.0)
    max_retries: int = 3

    selenium_emulate_mobile_default: bool = True
    selenium_wait_time_default: int = 10
    selenium_scroll_iterations_default: int = 10
    selenium_scroll_wait_time_default: int = 2
```

## 🎯 Verwendung

### 1. Server starten
```bash
  cd projekt
  python -m projekt.main
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


**Hakon**
- Student der Wirtschaftsinformatik - Informationstechnologie an der HM München
- GitHub: [@hakon-username](https://github.com/hakon-username)
- Mail: hakon.wahl@gmail.com