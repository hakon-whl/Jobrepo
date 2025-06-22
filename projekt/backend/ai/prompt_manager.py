import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptManager:
    """Verwaltet und lädt Prompt-Templates aus Dateien"""

    def __init__(self, prompts_directory: str):
        self.prompts_directory = Path(prompts_directory)
        # self._prompt_cache: Dict[str, str] = {} # Dieser Teil wurde entfernt
        self._validate_prompts_directory()

    def _validate_prompts_directory(self) -> None:
        """Validiert das Prompts-Verzeichnis"""
        if not self.prompts_directory.exists():
            logger.error(f"Prompts-Verzeichnis existiert nicht: {self.prompts_directory}")
            raise FileNotFoundError(f"Prompts-Verzeichnis nicht gefunden: {self.prompts_directory}")

        if not self.prompts_directory.is_dir():
            logger.error(f"Prompts-Pfad ist kein Verzeichnis: {self.prompts_directory}")
            raise NotADirectoryError(f"Prompts-Pfad ist kein Verzeichnis: {self.prompts_directory}")

    def _load_prompt_from_file(self, prompt_name: str) -> str:
        """Lädt einen Prompt aus einer Datei"""
        prompt_file = self.prompts_directory / f"{prompt_name}.txt"

        if not prompt_file.exists():
            available_prompts = self.get_available_prompts()
            logger.error(f"Prompt-Datei nicht gefunden: {prompt_file}")
            logger.info(f"Verfügbare Prompts: {available_prompts}")
            raise FileNotFoundError(f"Prompt-Datei nicht gefunden: {prompt_file}")

        try:
            with open(prompt_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                logger.debug(f"Prompt '{prompt_name}' erfolgreich geladen ({len(content)} Zeichen)")
                return content
        except Exception as e:
            logger.error(f"Fehler beim Laden der Prompt-Datei '{prompt_file}': {e}")
            raise

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Holt einen Prompt und ersetzt Platzhalter
        """
        prompt_template = self._load_prompt_from_file(prompt_name) # Jetzt wird immer neu geladen

        # Ersetze Platzhalter
        try:
            formatted_prompt = prompt_template.format(**kwargs)
            logger.debug(f"Prompt '{prompt_name}' erfolgreich formatiert mit {len(kwargs)} Variablen")
            return formatted_prompt
        except KeyError as e:
            logger.error(f"Fehlender Platzhalter in Prompt '{prompt_name}': {e}")
            logger.debug(f"Verfügbare Variablen: {list(kwargs.keys())}")
            raise ValueError(f"Fehlender Platzhalter in Prompt '{prompt_name}': {e}")
        except Exception as e:
            logger.error(f"Fehler beim Formatieren des Prompts '{prompt_name}': {e}")
            raise

    def get_available_prompts(self) -> list:
        """Gibt eine Liste aller verfügbaren Prompts zurück"""
        if not self.prompts_directory.exists():
            return []

        prompts = []
        for file_path in self.prompts_directory.glob("*.txt"):
            prompts.append(file_path.stem)

        return sorted(prompts)