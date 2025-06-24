import React, { useState, useMemo } from "react";
import PropTypes from "prop-types";
import { useForm, Controller } from "react-hook-form";
import { JOB_SITES, DISCIPLINES } from "../constants/enums";
import SkillsManager from "./SkillsManager";
import { extractTextFromPdfBlob } from "../services/pdf";

/**
 * Hauptformular für die Bewerbungsdaten-Erfassung
 * Sammelt alle relevanten Informationen und verarbeitet PDF-Uploads
 */
function ApplicationForm({
  onSubmit,
  isSubmitting,
  locationsData,
  availableSkills,
  onSkillsUpdate
}) {
  // React Hook Form Setup mit Standardwerten
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm({
    defaultValues: {
      jobTitle: "",
      location: "",
      discipline: "",
      radius: 20,
      jobSites: "",
      studyInfo: "",
      interests: "",
      skills: []
    }
  });

  // Überwachung spezifischer Formularfelder für dynamische UI-Updates
  const radius = watch("radius");
  const selectedLocation = watch("location");

  // Dynamisches Label für Radius basierend auf ausgewähltem Ort
  const selectedCityLabel =
    locationsData.find((l) => l.value === selectedLocation)?.label ||
    "Ort wählen";

  // Skills-Suchfunktionalität
  const [skillSearch, setSkillSearch] = useState("");
  const filteredSkills = useMemo(() => {
    if (!skillSearch.trim()) return availableSkills;
    return availableSkills.filter((skill) =>
      skill.label.toLowerCase().includes(skillSearch.toLowerCase())
    );
  }, [skillSearch, availableSkills]);

  // State für PDF-Datei-Uploads
  const [selectedFiles, setSelectedFiles] = useState([]);

  /**
   * Formular-Submit-Handler
   * Extrahiert Text aus PDFs und fügt ihn zu den Formulardaten hinzu
   */
  const submitHandler = async (data) => {
    const pdfContents = {};

    // PDF-Text-Extraktion für jede hochgeladene Datei
    for (const file of selectedFiles) {
      try {
        pdfContents[file.name] = await extractTextFromPdfBlob(file);
      } catch (e) {
        pdfContents[file.name] = `FEHLER_BEIM_EXTRAHIEREN: ${e.message}`;
      }
    }

    // Weiterleitung an Parent-Komponente mit erweiterten Daten
    onSubmit({ ...data, pdfContents });
  };

  return (
    <form onSubmit={handleSubmit(submitHandler)} className="application-form">
      {/* Jobsuche-Sektion */}
      <fieldset>
        <legend>Jobsuche</legend>

        <div className="form-group">
          <label htmlFor="jobTitle">Jobtitel*</label>
          <input
            id="jobTitle"
            {...register("jobTitle", { required: "Pflichtfeld" })}
          />
          {errors.jobTitle && <p>{errors.jobTitle.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="location">Stadt*</label>
          <select
            id="location"
            {...register("location", { required: "Pflichtfeld" })}
          >
            <option value="">Bitte wählen…</option>
            {locationsData.map((loc) => (
              <option key={loc.value} value={loc.value}>
                {loc.label}
              </option>
            ))}
          </select>
          {errors.location && <p>{errors.location.message}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="discipline">Disziplin</label>
          <select id="discipline" {...register("discipline")}>
            <option value="">(optional)</option>
            {DISCIPLINES.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        {/* Radius-Slider mit dynamischem Label */}
        <div className="form-group">
          <label htmlFor="radius">
            Radius: {radius} km (Basis: {selectedCityLabel})
          </label>
          <Controller
            name="radius"
            control={control}
            render={({ field }) => (
              <input
                type="range"
                id="radius"
                min="0"
                max="100"
                step="10"
                {...field}
              />
            )}
          />
        </div>

        <div className="form-group">
          <label htmlFor="jobSites">Jobseite*</label>
          <select
            id="jobSites"
            {...register("jobSites", { required: "Pflichtfeld" })}
          >
            <option value="">Bitte wählen…</option>
            {JOB_SITES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
          {errors.jobSites && <p>{errors.jobSites.message}</p>}
        </div>
      </fieldset>

      {/* Persönliche Daten und Dokumente */}
      <fieldset>
        <legend>Persönliches & Dokumente</legend>

        <div className="form-group">
          <label htmlFor="studyInfo">Studium Infos</label>
          <textarea id="studyInfo" {...register("studyInfo")} rows="3" />
        </div>

        <div className="form-group">
          <label htmlFor="interests">Interessen</label>
          <textarea id="interests" {...register("interests")} rows="3" />
        </div>

        {/* Skills-Manager für benutzerdefinierte Skills */}
        <div className="form-group">
          <SkillsManager
            availableSkills={availableSkills}
            onSkillsUpdate={onSkillsUpdate}
          />
        </div>

        {/* Skills-Auswahl mit Suchfunktion */}
        <div className="form-group">
          <label>Fähigkeiten auswählen (Mehrfachauswahl):</label>
          <div className="skills-search">
            <input
              type="text"
              placeholder="Skills suchen..."
              value={skillSearch}
              onChange={(e) => setSkillSearch(e.target.value)}
              aria-label="Skills suchen"
            />
          </div>
          <div className="checkbox-group" role="group" aria-label="Skills">
            {filteredSkills.map((skill) => (
              <div key={skill.value} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`skill-${skill.value}`}
                  value={skill.value}
                  {...register("skills")}
                />
                <label htmlFor={`skill-${skill.value}`}>{skill.label}</label>
              </div>
            ))}
          </div>
        </div>

        {/* PDF-Upload mit Dateifilterung */}
        <div className="form-group file-upload-group">
          <label htmlFor="documentUpload">PDFs hochladen</label>
          <input
            type="file"
            id="documentUpload"
            accept=".pdf"
            multiple
            className="file-input-hidden"
            onChange={(e) =>
              setSelectedFiles(
                Array.from(e.target.files).filter(
                  (f) => f.type === "application/pdf"
                )
              )
            }
          />
          <label htmlFor="documentUpload" className="file-upload-button">
            📁 Dateien auswählen
          </label>
          <div className="file-name-display">
            {selectedFiles.length > 0 ? (
              <ul>
                {selectedFiles.map((f, i) => (
                  <li key={i}>{f.name}</li>
                ))}
              </ul>
            ) : (
              "Keine Dateien ausgewählt"
            )}
          </div>
        </div>
      </fieldset>

      <button
        type="submit"
        disabled={isSubmitting}
        className="submit-button"
      >
        {isSubmitting ? "Sende…" : "Bewerbung senden"}
      </button>
    </form>
  );
}

ApplicationForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired,
  locationsData: PropTypes.array.isRequired,
  availableSkills: PropTypes.array.isRequired,
  onSkillsUpdate: PropTypes.func.isRequired
};

export default ApplicationForm;
