import { useState, useCallback } from 'react';
import { BASE_SKILLS, loadCustomSkillsFromStorage, saveCustomSkillsToStorage } from '../constants/enums';

/**
 * Custom Hook für Skills-Management
 * Verwaltet sowohl Base Skills als auch benutzerdefinierte Skills
 * Bietet Persistierung über localStorage
 */
export const useSkills = () => {
  // Initialisierung des Skills-State mit Base + Custom Skills
  const [allSkills, setAllSkills] = useState(() => {
    const customSkills = loadCustomSkillsFromStorage();
    return [...BASE_SKILLS, ...customSkills];
  });

  /**
   * Hauptfunktion zur Aktualisierung der Skills-Liste
   * Separiert Custom Skills und speichert sie persistent
   */
  const updateSkills = useCallback((newSkillsList) => {
    // Filtere nur die benutzerdefinierten Skills (nicht in BASE_SKILLS enthalten)
    const customSkills = newSkillsList.filter(skill =>
      !BASE_SKILLS.some(baseSkill => baseSkill.value === skill.value)
    );

    // Persistiere nur die Custom Skills
    saveCustomSkillsToStorage(customSkills);

    // Aktualisiere den lokalen State mit der vollständigen Liste
    setAllSkills(newSkillsList);
  }, []);

  /**
   * Fügt einen neuen Skill zur Liste hinzu
   */
  const addSkill = useCallback((newSkill) => {
    const updatedSkills = [...allSkills, newSkill];
    updateSkills(updatedSkills);
  }, [allSkills, updateSkills]);

  /**
   * Entfernt einen Skill aus der Liste
   * Base Skills können nicht gelöscht werden
   */
  const removeSkill = useCallback((skillValue) => {
    // Schutz für Base Skills
    const isBaseSkill = BASE_SKILLS.some(skill => skill.value === skillValue);
    if (isBaseSkill) {
      console.warn('Base Skills können nicht gelöscht werden:', skillValue);
      return;
    }

    const updatedSkills = allSkills.filter(skill => skill.value !== skillValue);
    updateSkills(updatedSkills);
  }, [allSkills, updateSkills]);

  /**
   * Setzt die Skills-Liste auf nur Base Skills zurück
   */
  const resetToBaseSkills = useCallback(() => {
    saveCustomSkillsToStorage([]);
    setAllSkills([...BASE_SKILLS]);
  }, []);

  return {
    allSkills, // Alle verfügbaren Skills (Base + Custom)
    baseSkills: BASE_SKILLS, // Nur die Base Skills
    customSkills: allSkills.filter(skill => // Nur die Custom Skills
      !BASE_SKILLS.some(baseSkill => baseSkill.value === skill.value)
    ),
    addSkill,
    removeSkill,
    updateSkills,
    resetToBaseSkills
  };
};