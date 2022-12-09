import os
import json
from typing import Dict
from pathlib import Path

CONFIG_FILE = Path.home() / ".smartarkivering" / "config.json"

CONFIG_KEYS = [
    "api_key",
    "submission_url",
    "default_destination"
]


def load_configuration() -> None:
    """Loads all CONFIG_KEYS if found in {Home}/.smartarkivering/config.json
    into envvars
    """

    if not CONFIG_FILE.is_file():
        raise FileNotFoundError("Konfigurationsfilen blev ikke fundet.")

    with open(CONFIG_FILE) as c:
        try:
            config: Dict = json.load(c)
        except ValueError as e:
            raise ValueError(f"Konfigurationsfilen kan ikke parses korrekt: {e}")
        else:
            for k, v in config.items():
                if k.lower() in CONFIG_KEYS:
                    os.environ[k.upper()] = str(v)
