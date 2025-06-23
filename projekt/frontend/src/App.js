import React, { useState } from "react";
import ApplicationForm from "./components/ApplicationForm";
import { submitApplicationData } from "./services/api";
import { LOCATIONS_DATA } from "./constants/enums";
import { useSkills } from "./hooks/useSkills";

function App() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const { allSkills, updateSkills } = useSkills();

  const handleFormSubmit = async (formData, files) => {
    setIsSubmitting(true);
    setSubmitStatus("loading");
    try {
      const result = await submitApplicationData({ ...formData, files });
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

      {/* <<< wieder mit .content-wrapper um das Form pad’n */}
      <div className="content-wrapper">
        <ApplicationForm
          onSubmit={handleFormSubmit}
          isSubmitting={isSubmitting}
          locationsData={LOCATIONS_DATA}
          availableSkills={allSkills}
          onSkillsUpdate={updateSkills}
        />

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