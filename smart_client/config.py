import os
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".smartarkivering" / "config.json"

REQUIRED_CONFIG_KEYS = [
    "api_key",
    "submission_url",
    "default_destination",
    "default_format",
    "default_hash",
    "archive_prefix",
]


def load_configuration() -> None:
    """Loads all required CONFIG_KEYS if found in {Home}/.smartarkivering/config.json
    into envvars
    """

    if not CONFIG_FILE.is_file():
        raise FileNotFoundError("Konfigurationsfilen blev ikke fundet.")

    with open(CONFIG_FILE) as c:
        try:
            config: dict = json.load(c)
        except ValueError as e:
            raise ValueError(f"FEJL. Konfigurationsfilen kan ikke parses korrekt: {e}")

        for key in REQUIRED_CONFIG_KEYS:
            if key not in config:
                raise ValueError(
                    f"FEJL. Mangler følgende påkrævede konfigurationsnøgle: {key}"
                )
            os.environ[key.upper()] = config[key]

            # for k, v in config.items():
            #     if k.lower() in REQUIRED_CONFIG_KEYS:
            #         os.environ[k.upper()] = str(v)
