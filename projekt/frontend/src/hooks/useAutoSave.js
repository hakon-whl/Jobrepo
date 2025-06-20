import { useState, useEffect, useCallback } from 'react';

const DRAFT_KEY = 'jobApplicationDraft';
const DRAFT_TIMESTAMP_KEY = 'jobApplicationDraftTimestamp';

export const useAutoSave = (formData, setFormData, delay = 2000) => {
  const [lastSaved, setLastSaved] = useState(null);
  const [draftExists, setDraftExists] = useState(false);

  // Prüfe beim Laden, ob ein Draft existiert
  useEffect(() => {
    const savedDraft = localStorage.getItem(DRAFT_KEY);
    const savedTimestamp = localStorage.getItem(DRAFT_TIMESTAMP_KEY);

    if (savedDraft && savedTimestamp) {
      setDraftExists(true);
      setLastSaved(new Date(savedTimestamp));
    }
  }, []);

  // Auto-Save mit Debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      // Nur speichern wenn mindestens ein Feld ausgefüllt ist
      const hasData = Object.values(formData).some(value => {
        if (Array.isArray(value)) return value.length > 0;
        return value && value.toString().trim() !== '';
      });

      if (hasData) {
        localStorage.setItem(DRAFT_KEY, JSON.stringify(formData));
        localStorage.setItem(DRAFT_TIMESTAMP_KEY, new Date().toISOString());
        setLastSaved(new Date());
        setDraftExists(true);
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [formData, delay]);

  const loadDraft = useCallback(() => {
    try {
      const savedDraft = localStorage.getItem(DRAFT_KEY);
      if (savedDraft) {
        const parsedDraft = JSON.parse(savedDraft);
        setFormData(parsedDraft);
        return true;
      }
    } catch (error) {
      console.error('Fehler beim Laden des Drafts:', error);
    }
    return false;
  }, [setFormData]);

  const clearDraft = useCallback(() => {
    localStorage.removeItem(DRAFT_KEY);
    localStorage.removeItem(DRAFT_TIMESTAMP_KEY);
    setDraftExists(false);
    setLastSaved(null);
  }, []);

  const getDraftAge = useCallback(() => {
    const savedTimestamp = localStorage.getItem(DRAFT_TIMESTAMP_KEY);
    if (savedTimestamp) {
      const saved = new Date(savedTimestamp);
      const now = new Date();
      const diffMinutes = Math.floor((now - saved) / (1000 * 60));

      if (diffMinutes < 1) return 'gerade eben';
      if (diffMinutes < 60) return `vor ${diffMinutes} Minuten`;

      const diffHours = Math.floor(diffMinutes / 60);
      if (diffHours < 24) return `vor ${diffHours} Stunden`;

      const diffDays = Math.floor(diffHours / 24);
      return `vor ${diffDays} Tagen`;
    }
    return null;
  }, []);

  return {
    lastSaved,
    draftExists,
    loadDraft,
    clearDraft,
    getDraftAge
  };
};