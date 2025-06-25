from pathlib import Path
from typing import List
from projekt.backend.core.config import app_config


class PromptManager:
    """
    Lädt Prompt-Templates aus dem Verzeichnis app_config.paths.prompts_dir
    und befüllt sie per str.format().
    """

    def __init__(self):
        # app_config.paths.prompts_dir ist bereits ein pathlib.Path
        self.prompts_directory: Path = app_config.paths.prompts_dir

    def _load_prompt(self, name: str) -> str:
        prompt_file = self.prompts_directory / f"{name}.txt"
        if not prompt_file.exists():
            available = self.get_available_prompts()
            raise FileNotFoundError(
                f"Prompt-Datei nicht gefunden: {prompt_file}. "
                f"Verfügbare Prompts: {available}"
            )
        return prompt_file.read_text(encoding="utf-8").strip()

    def get_prompt(self, name: str, **kwargs) -> str:
        template = self._load_prompt(name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Fehlender Platzhalter in '{name}.txt': {e}"
            )

    def get_available_prompts(self) -> List[str]:
        """Listet alle Prompt-Dateien (ohne .txt) sortiert auf."""
        return sorted(
            p.stem for p in self.prompts_directory.glob("*.txt")
        )