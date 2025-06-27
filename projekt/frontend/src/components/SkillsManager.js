import React, { useState } from 'react';
import PropTypes from 'prop-types';


const SkillsManager = ({ availableSkills, onSkillsUpdate }) => {
  const [newSkillLabel, setNewSkillLabel] = useState('');
  const [deleteMode, setDeleteMode] = useState(false);


  const handleAddSkill = () => {
    if (!newSkillLabel.trim()) {
      alert('Bitte einen Skill-Namen eingeben!');
      return;
    }

    const newSkillValue = generateValueFromLabel(newSkillLabel);

    const skillExists = availableSkills.some(
      skill => skill.value === newSkillValue || skill.label === newSkillLabel
    );

    if (skillExists) {
      alert('Dieser Skill existiert bereits!');
      return;
    }

    const newSkill = {
      value: newSkillValue,
      label: newSkillLabel
    };

    onSkillsUpdate([...availableSkills, newSkill]);
    setNewSkillLabel('');
  };

  const handleDeleteSkill = (skillToDelete) => {
    if (window.confirm(`Möchten Sie "${skillToDelete.label}" wirklich löschen?`)) {
      const updatedSkills = availableSkills.filter(
        skill => skill.value !== skillToDelete.value
      );
      onSkillsUpdate(updatedSkills);
    }
  };

  const generateValueFromLabel = (label) => {
    return label
      .toLowerCase()
      .replace(/[äöüß]/g, char => ({
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'
      }[char] || char))
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddSkill();
    }
  };

  const standardSkills = availableSkills.filter(skill =>
    ['javascript', 'python', 'java', 'react', 'html', 'css', 'sql', 'git',
     'nodejs', 'typescript', 'docker', 'cloud-basics', 'agile', 'angular',
     'c-sharp', 'machine-learning', 'mysql', 'linux', 'ci-cd', 'projektmanagement']
    .includes(skill.value)
  );

  const customSkills = availableSkills.filter(skill =>
    !standardSkills.some(stdSkill => stdSkill.value === skill.value)
  );

  return (
    <div className="skills-manager-modern">
      {/* Header mit Skill-Anzahl */}
      <div className="skills-manager-header">
        <h4>Eigene Skills verwalten</h4>
        <span className="skills-count">{customSkills.length}</span>
      </div>

      {/* Eingabebereich für neue Skills */}
      <div className="add-skill-section">
        <div className="add-skill-input-group">
          <input
            type="text"
            placeholder="Neuen Skill hinzufügen"
            value={newSkillLabel}
            onChange={(e) => setNewSkillLabel(e.target.value)}
            onKeyPress={handleKeyPress}
            className="add-skill-input"
          />
          <button
            type="button"
            onClick={handleAddSkill}
            className="add-skill-btn"
            disabled={!newSkillLabel.trim()}
          >
            Hinzufügen
          </button>
        </div>
      </div>

      {/* Liste der benutzerdefinierten Skills */}
      {customSkills.length > 0 && (
        <div className="custom-skills-section">
          <div className="custom-skills-header">
            <span className="custom-skills-title">Ihre eigenen Skills</span>
            <button
              type="button"
              onClick={() => setDeleteMode(!deleteMode)}
              className={`delete-toggle-btn ${deleteMode ? 'active' : ''}`}
            >
              {deleteMode ? 'Fertig' : 'Bearbeiten'}
            </button>
          </div>

          <div className="custom-skills-list">
            {customSkills.map(skill => (
              <div
                key={skill.value}
                className={`custom-skill-tag ${deleteMode ? 'delete-mode' : ''}`}
              >
                <span className="skill-name">{skill.label}</span>
                {deleteMode && (
                  <button
                    type="button"
                    onClick={() => handleDeleteSkill(skill)}
                    className="delete-skill-btn"
                    title={`${skill.label} löschen`}
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback-Nachricht wenn keine eigenen Skills vorhanden */}
      {customSkills.length === 0 && (
        <div className="no-custom-skills">
          <p>Fügen Sie eigene Skills hinzu, die in der Standard-Liste fehlen.</p>
        </div>
      )}
    </div>
  );
};

SkillsManager.propTypes = {
  availableSkills: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSkillsUpdate: PropTypes.func.isRequired,
};

export default SkillsManager;