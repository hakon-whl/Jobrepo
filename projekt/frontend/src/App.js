import React, { useState } from "react";
import ApplicationForm from "./components/ApplicationForm";
import { submitApplicationData } from "./services/api";
import { LOCATIONS_DATA } from "./constants/enums";
import { useSkills } from "./hooks/useSkills";

/**
 * PDF-Text-Extraktion direkt in App.js
 */
export const extractTextFromPdfBlob = async (file) => {
  try {
    // Dynamischer Import von PDF.js
    const pdfjsLib = await import('pdfjs-dist/build/pdf');

    // Worker konfigurieren
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://unpkg.com/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs';

    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
    let fullText = '';

    // Alle Seiten durchgehen
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += pageText + '\n';
    }

    return fullText.trim();
  } catch (error) {
    console.error('PDF-Extraktion fehlgeschlagen:', error);
    throw new Error(`PDF-Verarbeitung fehlgeschlagen: ${error.message}`);
  }
};

/**
 * Hauptkomponente der Bewerbungsanwendung
 * Koordiniert Formular-Submission und Skills-Management
 */
function App() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const { allSkills, updateSkills } = useSkills();

  /**
   * Handler für Formular-Submission
   * Verarbeitet die Bewerbungsdaten inklusive PDF-Inhalte
   */
  const handleFormSubmit = async (data) => {
    setIsSubmitting(true);
    setSubmitStatus("loading");

    try {
      const result = await submitApplicationData(data);
      console.log("Ergebnis:", result);
      setSubmitStatus("success");
    } catch (err) {
      console.error(err);
      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Bewerbungsdaten Erfassen und Senden</h1>
      <div className="content-wrapper">
        <ApplicationForm
          onSubmit={handleFormSubmit}
          isSubmitting={isSubmitting}
          locationsData={LOCATIONS_DATA}
          availableSkills={allSkills}
          onSkillsUpdate={updateSkills}
        />
        {/* Status-Feedback für den Benutzer */}
        {submitStatus && (
          <p className={`status-message ${submitStatus}`}>
            {submitStatus === "loading"
              ? "Lädt..."
              : submitStatus === "success"
              ? "Erfolgreich gesendet!"
              : "Fehler beim Senden!"}
          </p>
        )}
      </div>
    </div>
  );
}

export default App;