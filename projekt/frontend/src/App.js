// src/App.js
import React, { useState, useCallback, useMemo } from "react";
import ApplicationForm from "./components/ApplicationForm";
import { submitApplicationData } from "./services/api";
import "./App.css";
import {
  LOCATIONS_DATA,
  JOB_SITES,
  SKILLS,
  DISCIPLINES,
} from "./constants/enums";
import { extractTextFromPdfBlob } from "./utils/pdfToTxt";

const initialFormData = {
  jobTitle: "",
  location: "",
  selectedPlz: "",
  discipline: "",
  radius: 20,
  jobSites: "",
  studyInfo: "",
  interests: "",
  skills: [],
};

function App() {
  const [formData, setFormData] = useState(initialFormData);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [submitMessage, setSubmitMessage] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // --- handleChange angepasst ---
  const handleChange = useCallback((event) => {
    const { name, value, type } = event.target;

    if (type === "checkbox" && name === "skills") {
      // Skills-Logik bleibt gleich
      const skillValue = value;
      setFormData((prevData) => ({
        ...prevData,
        skills: prevData.skills.includes(skillValue)
          ? prevData.skills.filter((skill) => skill !== skillValue)
          : [...prevData.skills, skillValue],
      }));
    } else if (name === "location") {
      // Wenn die Stadt geändert wird, PLZ zurücksetzen
      setFormData((prevData) => ({
        ...prevData,
        location: value,
        selectedPlz: "", // Wichtig: PLZ zurücksetzen!
        radius: prevData.radius, // Radius beibehalten oder auch zurücksetzen? Hier beibehalten.
      }));
    } else {
      // Alle anderen Felder (inkl. selectedPlz) normal aktualisieren
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  }, []);

  const handleSliderChange = useCallback((event) => {
    setFormData((prevData) => ({
      ...prevData,
      radius: parseInt(event.target.value, 10),
    }));
  }, []);

  const handleFileChange = useCallback((event) => {
    // ... (unverändert)
    const files = event.target.files;
    setSubmitStatus(null);
    if (files && files.length > 0) {
      const pdfFiles = Array.from(files).filter(
        (file) => file.type === "application/pdf",
      );
      if (pdfFiles.length !== files.length) {
        alert(
          "Einige ausgewählte Dateien waren keine PDFs und wurden ignoriert.",
        );
      }
      setUploadedFiles(pdfFiles);
    } else {
      setUploadedFiles([]);
    }
  }, []);

  // --- handleSubmit angepasst (nur dataToSend) ---
  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus("loading");
    setSubmitMessage("Prüfe Daten und verarbeite PDFs...");

    const extractedPdfsData = {};
    // ... (PDF Extraktion bleibt gleich) ...
    if (uploadedFiles && uploadedFiles.length > 0) {
      console.log(`Starte Extraktion für ${uploadedFiles.length} PDF(s)...`);
      try {
        await Promise.all(
          uploadedFiles.map(async (file) => {
            try {
              console.log(` - Extrahiere ${file.name}`);
              const text = await extractTextFromPdfBlob(file);
              extractedPdfsData[file.name] = text;
              console.log(`   -> ${file.name} erfolgreich extrahiert.`);
            } catch (fileError) {
              console.error(
                `Fehler beim Extrahieren von ${file.name}:`,
                fileError,
              );
              extractedPdfsData[file.name] = `FEHLER_BEIM_EXTRAHIEREN: ${fileError.message || "Unbekannter Fehler"}`;
            }
          }),
        );
        console.log("Alle PDFs erfolgreich verarbeitet (oder Fehler notiert).");
        setSubmitMessage("PDFs verarbeitet, sende Daten...");
      } catch (overallError) {
        console.error("Fehler während der PDF-Verarbeitung:", overallError);
        setSubmitStatus("error");
        setSubmitMessage(
          `Fehler bei PDF-Verarbeitung: ${overallError.message || "Unbekannter Fehler"}. Versand abgebrochen.`,
        );
        setIsSubmitting(false);
        return;
      }
    } else {
      console.log("Keine PDF-Dateien zum Extrahieren vorhanden.");
      setSubmitMessage("Sende Daten (ohne PDF-Inhalte)...");
    }

    // Datenobjekt für das Backend: Enthält jetzt location und selectedPlz
    const dataToSend = {
      ...formData, // Enthält jobTitle, location, selectedPlz, discipline, radius, etc.
      skills: formData.skills, // Explizit, falls nicht in ...formData überschrieben
      pdfContents: extractedPdfsData,
    };

    // Backend-Aufruf bleibt gleich
    try {
      console.log("Sende folgendes Objekt an das Backend:", dataToSend);
      const responseData = await submitApplicationData(dataToSend);
      setSubmitStatus("success");
      setSubmitMessage(responseData.message || "Daten erfolgreich übermittelt!");
    } catch (error) {
      console.error("Fehler beim Senden der Daten an das Backend:", error);
      setSubmitStatus("error");
      setSubmitMessage(
        error.message ||
          "Fehler beim Senden der Daten. Bitte versuchen Sie es erneut.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Memoized Wert für die aktuell ausgewählte Stadt (Objekt)
  const selectedCityData = useMemo(() => {
    return LOCATIONS_DATA.find((loc) => loc.value === formData.location);
  }, [formData.location]);

  return (
    <div className="app-container">
      <h1>Bewerbungsdaten Erfassen und Senden</h1>
      <div className="content-wrapper">
        <div className="form-section">
          <ApplicationForm
            formData={formData}
            onChange={handleChange}
            onSliderChange={handleSliderChange}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
            onFileChange={handleFileChange}
            selectedFiles={uploadedFiles}
            // Übergeben Sie die neuen Daten und das gefundene Stadtobjekt
            locationsData={LOCATIONS_DATA}
            selectedCityData={selectedCityData}
          />

          {/* Statusanzeige mit verbesserter Darstellung */}
          {submitStatus && (
            submitStatus === "success" ? (
              <button
                className="status-button"
                onClick={() => {
                  // Optional: Formular zurücksetzen oder andere Aktionen
                  setFormData(initialFormData);
                  setSubmitStatus(null);
                  setUploadedFiles([]);
                }}
              >
                <span role="img" aria-label="Erfolg">✓</span> {submitMessage} - PDF wurde heruntergeladen
              </button>
            ) : (
              <p className={`status-message ${submitStatus}`}>
                {submitStatus === "loading" ? (
                  <>
                    <span role="img" aria-label="Lädt">⏳</span> {submitMessage}
                  </>
                ) : (
                  <>
                    <span role="img" aria-label="Fehler">⚠️</span> {submitMessage}
                  </>
                )}
              </p>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
