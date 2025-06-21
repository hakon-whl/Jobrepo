import React, { useState, useMemo } from "react";
import PropTypes from "prop-types";
import { JOB_SITES, DISCIPLINES } from "../constants/enums";
import SkillsManager from "./SkillsManager";

function ApplicationForm({
  formData,
  onChange,
  onSliderChange,
  onSubmit,
  isSubmitting,
  onFileChange,
  selectedFiles,
  locationsData,
  selectedCityData,
  availableSkills,
  onSkillsUpdate,
}) {
  const selectedCityLabel = selectedCityData?.label || "Ort wählen";

  // State für die Skills-Suche
  const [skillSearchQuery, setSkillSearchQuery] = useState("");

  // Gefilterte Skills basierend auf der Suchanfrage
  const filteredSkills = useMemo(() => {
    if (!skillSearchQuery.trim()) return availableSkills;

    return availableSkills.filter((skill) =>
      skill.label.toLowerCase().includes(skillSearchQuery.toLowerCase())
    );
  }, [skillSearchQuery, availableSkills]);

  return (
    <form onSubmit={onSubmit} className="application-form">
      {/* Jobsuche Fieldset */}
      <fieldset>
        <legend>Jobsuche</legend>
        <div className="form-group">
          <label htmlFor="jobTitle">Jobtitel (Suchbegriff):</label>
          <input
            type="text"
            id="jobTitle"
            name="jobTitle"
            value={formData.jobTitle}
            onChange={onChange}
            required
            aria-required="true"
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Stadt:</label>
          <select
            id="location"
            name="location"
            value={formData.location}
            onChange={onChange}
            required
            aria-required="true"
          >
            <option value="" disabled>
              Bitte wählen...
            </option>
            {locationsData.map((loc) => (
              <option key={loc.value} value={loc.value}>
                {loc.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="discipline">Disziplin:</label>
          <select
            id="discipline"
            name="discipline"
            value={formData.discipline}
            onChange={onChange}
          >
            <option value="">Bitte wählen (optional)...</option>
            {DISCIPLINES.map((disc) => (
              <option key={disc.value} value={disc.value}>
                {disc.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="radius">
            Radius: {formData.radius} km (Basis: {selectedCityLabel})
          </label>
          <input
            type="range"
            id="radius"
            name="radius"
            min="0"
            max="100"
            step="10"
            value={formData.radius}
            onChange={onSliderChange}
            disabled={!formData.location}
            aria-valuemin="0"
            aria-valuemax="100"
            aria-valuenow={formData.radius}
          />
        </div>

        <div className="form-group">
          <label htmlFor="jobSites">Bevorzugte Jobseiten:</label>
          <select
            id="jobSites"
            name="jobSites"
            value={formData.jobSites}
            onChange={onChange}
            required
            aria-required="true"
          >
            <option value="" disabled>
              Bitte wählen...
            </option>
            {JOB_SITES.map((site) => (
              <option key={site.value} value={site.value}>
                {site.label}
              </option>
            ))}
          </select>
        </div>
      </fieldset>

      {/* Persönliche Angaben & Dokumente Fieldset */}
      <fieldset>
        <legend>Persönliche Angaben & Dokumente</legend>
        <div className="form-group">
          <label htmlFor="studyInfo">Studium Infos:</label>
          <textarea
            id="studyInfo"
            name="studyInfo"
            value={formData.studyInfo}
            onChange={onChange}
            placeholder="z.B. B.Sc. Informatik, Lieblingsmodule: KI, WebDev"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="interests">Interessen:</label>
          <textarea
            id="interests"
            name="interests"
            value={formData.interests}
            onChange={onChange}
            placeholder="z.b. Open Source, Klettern, Fotografie"
            rows="3"
          />
        </div>

        {/* *** MODERNER SKILLS MANAGER *** */}
        <div className="form-group">
          <SkillsManager
            availableSkills={availableSkills}
            onSkillsUpdate={onSkillsUpdate}
          />
        </div>

        <div className="form-group">
          <label>Fähigkeiten auswählen (Mehrfachauswahl):</label>

          <div className="skills-search">
            <input
              type="text"
              placeholder="Skills suchen..."
              value={skillSearchQuery}
              onChange={(e) => setSkillSearchQuery(e.target.value)}
              aria-label="Skills suchen"
            />
          </div>

          <div className="checkbox-group" role="group" aria-label="Fähigkeiten">
            {filteredSkills.map((skill) => (
              <div key={skill.value} className="checkbox-item">
                <input
                  type="checkbox"
                  id={`skill-${skill.value}`}
                  name="skills"
                  value={skill.value}
                  checked={formData.skills.includes(skill.value)}
                  onChange={onChange}
                />
                <label htmlFor={`skill-${skill.value}`}>{skill.label}</label>
              </div>
            ))}
          </div>
        </div>

        <div className="form-group file-upload-group">
          <label htmlFor="documentUploadInput">
            Dokumente hochladen (PDFs):
          </label>
          <input
            type="file"
            id="documentUploadInput"
            name="documents"
            accept=".pdf"
            multiple
            onChange={onFileChange}
            className="file-input-hidden"
          />
          <label htmlFor="documentUploadInput" className="file-upload-button">
            📁 Dateien auswählen
          </label>
          <div className="file-name-display">
            {selectedFiles && selectedFiles.length > 0 ? (
              <ul>
                {selectedFiles.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            ) : (
              "Keine Dateien ausgewählt"
            )}
          </div>
        </div>
      </fieldset>

      <button type="submit" disabled={isSubmitting} className="submit-button">
        {isSubmitting ? "Sende..." : "Bewerbungsdaten Senden"}
      </button>
    </form>
  );
}

ApplicationForm.propTypes = {
  formData: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onSliderChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired,
  onFileChange: PropTypes.func,
  selectedFiles: PropTypes.arrayOf(PropTypes.instanceOf(File)),
  locationsData: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  selectedCityData: PropTypes.shape({
    value: PropTypes.string,
    label: PropTypes.string,
  }),
  availableSkills: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSkillsUpdate: PropTypes.func.isRequired,
};

ApplicationForm.defaultProps = {
  onFileChange: () => {},
  selectedFiles: [],
  selectedCityData: null,
};

export default ApplicationForm;