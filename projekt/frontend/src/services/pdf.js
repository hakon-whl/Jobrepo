import React, { useState } from "react";
import ApplicationForm from "./components/ApplicationForm";
import { submitApplicationData } from "./services/api";
import { LOCATIONS_DATA } from "./constants/enums";
import { useSkills } from "./hooks/useSkills";

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