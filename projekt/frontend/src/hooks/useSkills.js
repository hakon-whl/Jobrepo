import { useState, useCallback } from 'react';
import { BASE_SKILLS, loadCustomSkillsFromStorage, saveCustomSkillsToStorage } from '../constants/enums';


export const useSkills = () => {

  const [allSkills, setAllSkills] = useState(() => {
    const customSkills = loadCustomSkillsFromStorage();
    return [...BASE_SKILLS, ...customSkills];
  });


  const updateSkills = useCallback((newSkillsList) => {

    const customSkills = newSkillsList.filter(skill =>
      !BASE_SKILLS.some(baseSkill => baseSkill.value === skill.value)
    );

    saveCustomSkillsToStorage(customSkills);


    setAllSkills(newSkillsList);
  }, []);


  const addSkill = useCallback((newSkill) => {
    const updatedSkills = [...allSkills, newSkill];
    updateSkills(updatedSkills);
  }, [allSkills, updateSkills]);


  const removeSkill = useCallback((skillValue) => {
    const isBaseSkill = BASE_SKILLS.some(skill => skill.value === skillValue);
    if (isBaseSkill) {
      console.warn('Base Skills können nicht gelöscht werden:', skillValue);
      return;
    }

    const updatedSkills = allSkills.filter(skill => skill.value !== skillValue);
    updateSkills(updatedSkills);
  }, [allSkills, updateSkills]);

  const resetToBaseSkills = useCallback(() => {
    saveCustomSkillsToStorage([]);
    setAllSkills([...BASE_SKILLS]);
  }, []);

  return {
    allSkills,
    baseSkills: BASE_SKILLS,
    customSkills: allSkills.filter(skill =>
      !BASE_SKILLS.some(baseSkill => baseSkill.value === skill.value)
    ),
    addSkill,
    removeSkill,
    updateSkills,
    resetToBaseSkills
  };
};