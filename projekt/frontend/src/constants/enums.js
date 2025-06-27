// Statische Datendefinitionen für Formular-Optionen
export const LOCATIONS_DATA = [
  { value: "berlin", label: "Berlin" },
  { value: "braunschweig", label: "Braunschweig" },
  { value: "bremen", label: "Bremen" },
  { value: "bremerhaven", label: "Bremerhaven" },
  { value: "cottbus", label: "Cottbus" },
  { value: "dresden", label: "Dresden" },
  { value: "duesseldorf", label: "Düsseldorf" },
  { value: "erfurt", label: "Erfurt" },
  { value: "frankfurt-am-main", label: "Frankfurt am Main" },
  { value: "halle-saale", label: "Halle (Saale)" },
  { value: "hamburg", label: "Hamburg" },
  { value: "hannover", label: "Hannover" },
  { value: "jena", label: "Jena" },
  { value: "karlsruhe", label: "Karlsruhe" },
  { value: "kiel", label: "Kiel" },
  { value: "koeln", label: "Köln" },
  { value: "leipzig", label: "Leipzig" },
  { value: "luebeck", label: "Lübeck" },
  { value: "ludwigshafen-am-rhein", label: "Ludwigshafen am Rhein" },
  { value: "magdeburg", label: "Magdeburg" },
  { value: "mainz", label: "Mainz" },
  { value: "munich", label: "München" },
  { value: "neunkirchen", label: "Neunkirchen" },
  { value: "nuernberg", label: "Nürnberg" },
  { value: "potsdam", label: "Potsdam" },
  { value: "rostock", label: "Rostock" },
  { value: "saarbruecken", label: "Saarbrücken" },
  { value: "schwerin", label: "Schwerin" },
  { value: "stuttgart", label: "Stuttgart" },
  { value: "wiesbaden", label: "Wiesbaden" },
];

export const JOB_SITES = [
  { value: "StepStone", label: "StepStone" },
  { value: "Xing", label: "Xing" },
];

export const DISCIPLINES = [
  { value: "IT", label: "IT" },
  { value: "Marketing", label: "Marketing" },
  { value: "Vertrieb und Verkauf", label: "Vertrieb und Verkauf" },
  { value: "Medien", label: "Medien" },
  { value: "Bildung", label: "Bildung" },
  { value: "Beratung", label: "Beratung" },
  { value: "Management", label: "Management" },
  { value: "Administration", label: "Administration" },
  { value: "Personal", label: "Personal" },
  { value: "Buchhaltung", label: "Buchhaltung" },
  { value: "Ingenieurwesen", label: "Ingenieurwesen" },
  { value: "Kundenservice", label: "Kundenservice" },
  { value: "Finanzen", label: "Finanzen" },
  { value: "Logistik", label: "Logistik" },
  { value: "Wissenschaften", label: "Wissenschaften" },
  { value: "Bauwesen", label: "Bauwesen" },
  { value: "Banken", label: "Banken" },
  { value: "Gastronomie, Hotellerie", label: "Gastronomie, Hotellerie" },
  { value: "Gesundheit", label: "Gesundheit" },
  { value: "Groß- und Einzelhandel", label: "Groß- und Einzelhandel" },
];

// Vordefinierte Standard-Skills (nicht löschbar)
export const BASE_SKILLS = [
  { value: "javascript", label: "JavaScript" },
  { value: "python", label: "Python" },
  { value: "java", label: "Java" },
  { value: "react", label: "React" },
  { value: "html", label: "HTML" },
  { value: "css", label: "CSS" },
  { value: "sql", label: "SQL" },
  { value: "git", label: "Git" },
  { value: "nodejs", label: "Node.js" },
  { value: "typescript", label: "TypeScript" },
  { value: "docker", label: "Docker" },
  { value: "cloud-basics", label: "Cloud Computing (AWS/Azure/GCP)" },
  { value: "agile", label: "Agile Methoden" },
  { value: "angular", label: "Angular" },
  { value: "c-sharp", label: "C#" },
  { value: "machine-learning", label: "Machine Learning" },
  { value: "mysql", label: "MySQL/PostgreSQL" },
  { value: "linux", label: "Linux/Unix" },
  { value: "ci-cd", label: "CI/CD" },
  { value: "projektmanagement", label: "Projektmanagement" },
];

/**
 * Lädt benutzerdefinierte Skills aus dem localStorage
 * @returns {Array} Array von Custom Skills oder leeres Array bei Fehlern
 */
export const loadCustomSkillsFromStorage = () => {
  try {
    const storedSkills = localStorage.getItem('customSkills');
    return storedSkills ? JSON.parse(storedSkills) : [];
  } catch (error) {
    console.error('Fehler beim Laden der Custom Skills:', error);
    return [];
  }
};

/**
 * Speichert benutzerdefinierte Skills im localStorage
 * @param {Array} customSkills - Array von Custom Skills zum Speichern
 */
export const saveCustomSkillsToStorage = (customSkills) => {
  try {
    localStorage.setItem('customSkills', JSON.stringify(customSkills));
  } catch (error) {
    console.error('Fehler beim Speichern der Custom Skills:', error);
  }
};

/**
 * Kombiniert Base Skills mit benutzerdefinierten Skills
 * @returns {Array} Vollständige Liste aller verfügbaren Skills
 */
export const getAllSkills = () => {
  const customSkills = loadCustomSkillsFromStorage();
  return [...BASE_SKILLS, ...customSkills];
};