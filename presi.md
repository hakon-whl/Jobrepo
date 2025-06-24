# Presentationen Leitfaden
Projekt für das Skrapten von Job auf Jobwebseiten
### Idee und Punkte

- Probleme beim Bewerben, keine rückmeldungen, und niedrige Conversionrate von Bewerbung und Bewerbungsgespräch, aus erfahrung vielleicht 10%
- Dachte Quantität über qualitäet, da war ich richtig durch die 10% deswegen optimierte suche nach Jobs und vorsortierung mit Anschreiben, wenn Job einem gut gefällt kann man das Anschreiben anpassen
- Jede neue Jobwebseite muss man sich neu regestrieren um Jobs für einen selber zu finden

#### Vorführung

### Hervorheben

- Eigenständiges verwalten der Fähigkeiten durch Speichern der Userfähigkeiten im localStorage des Browsers
- Verarbeitung von Lazyload Webseiten mithilfe von Selenium
- Configurieung alles Tools der Anwendung über das Config File
- Überarbeitung der Url verarbeitung, davor für jede Url direkte verarbeitung, jetzt sammel von allen und dann alle in Summe vearbeiten
### Verbesserung

- Das Zusammenbringen der jeweiligen Jobwebseiten, aussschließen von Duplikaten (ganzes Bild für den Jobmarkt)
- Optimirung der Runtime durch Async Implementierung beim Scrapen und Jobinfo verarbeitung in kombi mit Playwright-Bibliothek durch lernen aus history
- Speicherung der verarbeiteten Job Files in individualisierten ordner

### Code

self.headless = headless
    if self.headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={width},{height}")