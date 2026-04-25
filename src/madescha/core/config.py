from pathlib import Path
import os
from enum import Enum, auto

import confuse

APP_NAME = "madescha"

DEFAULTS = {
    "automatically_parse_opened_documents" : True,
    "export_root_directory": os.path.join(str(Path.home())),
    "export_format": "${date}__${author_short}__${title}"

}

class MadeschaConfig():
    """
    User configuration backed by confuse.
    Config file is automatically stored in the platform-appropriate directory:
      - Linux:   ~/.config/my_app/config.yaml
      - macOS:   ~/Library/Application Support/my_app/config.yaml
      - Windows: C:/Users/<user>/AppData/Local/my_app/config.yaml
    """

    def __init__(self) -> None:
        self._config = confuse.Configuration(APP_NAME, read=True)
        self._config.add(DEFAULTS)

    @property
    def config_file(self) -> Path:
        """Returns the path to the config file."""
        return Path(self._config.config_dir()) / confuse.CONFIG_FILENAME
    
    
    # automatically_parse_opened_documents

    @property
    def automatically_parse_opened_documents(self) -> bool:
        return self._config["automatically_parse_opened_documents"].get(bool)

    @automatically_parse_opened_documents.setter
    def automatically_parse_opened_documents(self, value: bool) -> None:
        self._config["automatically_parse_opened_documents"] = value

    # export_root_directory

    @property
    def export_root_directory(self) -> str:
        return self._config["export_root_directory"].get(str)

    @export_root_directory.setter
    def export_root_directory(self, value: str) -> None:
        self._config["export_root_directory"] = value
    
    # export_format

    @property
    def export_format(self) -> str:
        return self._config["export_format"].get(str)

    @export_format.setter
    def export_format(self, value: str) -> None:
        self._config["export_format"] = value
    


    def save(self) -> None:
        """Saves the current configuration to the config file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            f.write(self._config.dump())

    def __repr__(self) -> str:
        return (
            "Config("
            f"automatically_parse_opened_documents={self.automatically_parse_opened_documents!r}, "
            f"export_root_directory={self.export_root_directory!r}, "
            f"export_format={self.export_format!r}, "
        )
    


