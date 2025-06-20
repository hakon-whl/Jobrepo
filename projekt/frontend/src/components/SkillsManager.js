import React, { useState } from 'react';
import PropTypes from 'prop-types';

const SkillsManager = ({ availableSkills, onSkillsUpdate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [newSkillLabel, setNewSkillLabel] = useState('');
  const [newSkillValue, setNewSkillValue] = useState('');
  const [deleteMode, setDeleteMode] = useState(false);

  const handleAddSkill = () => {
    if (!newSkillLabel.trim() || !newSkillValue.trim()) {
      alert('Bitte sowohl Label als auch Wert eingeben!');
      return;
    }

    // Prüfe ob Skill bereits existiert
    const skillExists = availableSkills.some(
      skill => skill.value === newSkillValue || skill.label === newSkillLabel
    );

    if (skillExists) {
      alert('Dieser Skill existiert bereits!');
      return;
    }

    const newSkill = {
      value: newSkillValue.toLowerCase().replace(/\s+/g, '-'),
      label: newSkillLabel
    };

    onSkillsUpdate([...availableSkills, newSkill]);
    setNewSkillLabel('');
    setNewSkillValue('');
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

  const handleLabelChange = (e) => {
    const label = e.target.value;
    setNewSkillLabel(label);
    setNewSkillValue(generateValueFromLabel(label));
  };

  // Unterscheide zwischen Standard-Skills und Custom-Skills
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
    <div className="skills-manager">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="skills-manager-toggle"
      >
        🛠️ Skills verwalten {isOpen ? '▼' : '▶'}
      </button>

      {isOpen && (
        <div className="skills-manager-content">
          <div className="skills-manager-section">
            <h4>Neuen Skill hinzufügen</h4>
            <div className="add-skill-form">
              <div className="form-row">
                <input
                  type="text"
                  placeholder="Skill-Name (z.B. Vue.js)"
                  value={newSkillLabel}
                  onChange={handleLabelChange}
                  className="skill-input"
                />
                <input
                  type="text"
                  placeholder="Technischer Wert (z.B. vuejs)"
                  value={newSkillValue}
                  onChange={(e) => setNewSkillValue(e.target.value)}
                  className="skill-input"
                />
                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="add-skill-button"
                >
                  ➕ Hinzufügen
                </button>
              </div>
            </div>
          </div>

          <div className="skills-manager-section">
            <div className="delete-mode-toggle">
              <h4>Eigene Skills ({customSkills.length})</h4>
              <button
                type="button"
                onClick={() => setDeleteMode(!deleteMode)}
                className={`delete-mode-button ${deleteMode ? 'active' : ''}`}
              >
                {deleteMode ? '✅ Fertig' : '🗑️ Löschen'}
              </button>
            </div>

            {customSkills.length === 0 ? (
              <p className="no-custom-skills">Noch keine eigenen Skills hinzugefügt.</p>
            ) : (
              <div className="custom-skills-grid">
                {customSkills.map(skill => (
                  <div
                    key={skill.value}
                    className={`custom-skill-item ${deleteMode ? 'delete-mode' : ''}`}
                  >
                    <span className="skill-label">{skill.label}</span>
                    {deleteMode && (
                      <button
                        type="button"
                        onClick={() => handleDeleteSkill(skill)}
                        className="delete-skill-button"
                        title={`${skill.label} löschen`}
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="skills-manager-info">
            <small>
              💡 <strong>Info:</strong> Standard-Skills können nicht gelöscht werden.
              Eigene Skills werden lokal gespeichert und stehen beim nächsten Besuch zur Verfügung.
            </small>
          </div>
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