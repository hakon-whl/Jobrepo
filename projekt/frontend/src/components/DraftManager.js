import React from 'react';
import PropTypes from 'prop-types';

const DraftManager = ({ draftExists, onLoadDraft, onClearDraft, getDraftAge, lastSaved }) => {
  if (!draftExists) return null;

  const draftAge = getDraftAge();

  return (
    <div className="draft-manager">
      <div className="draft-notification">
        <div className="draft-info">
          <span className="draft-icon">💾</span>
          <div className="draft-text">
            <strong>Entwurf verfügbar</strong>
            <br />
            <small>Zuletzt gespeichert {draftAge}</small>
          </div>
        </div>
        <div className="draft-actions">
          <button
            type="button"
            onClick={onLoadDraft}
            className="draft-load-button"
          >
            📂 Laden
          </button>
          <button
            type="button"
            onClick={onClearDraft}
            className="draft-clear-button"
          >
            🗑️ Löschen
          </button>
        </div>
      </div>

      {lastSaved && (
        <div className="auto-save-indicator">
          <span className="auto-save-icon">✓</span>
          <small>Automatisch gespeichert um {lastSaved.toLocaleTimeString()}</small>
        </div>
      )}
    </div>
  );
};

DraftManager.propTypes = {
  draftExists: PropTypes.bool.isRequired,
  onLoadDraft: PropTypes.func.isRequired,
  onClearDraft: PropTypes.func.isRequired,
  getDraftAge: PropTypes.func.isRequired,
  lastSaved: PropTypes.instanceOf(Date),
};

export default DraftManager;