import os
import json
from pathlib import Path

# CONFIG_FILE = Path.home() / ".smartarkivering" / "config.json"

REQUIRED_CONFIG_KEYS = [
    "api_key",
    "submission_url",
    "default_destination",
    "default_format",
    "default_hash",
    "archive_prefix",
]


def load_configuration(conf_path: Path = None) -> None:
    """Loads all CONFIG_KEYS into envvars"""

    default_file: Path = Path.home() / ".smartarkivering" / "config.json"
    conf_file: Path

    if conf_path:
        if not conf_path.is_file():
            raise FileNotFoundError(f"Konfigurationsfilen findes ikke her: {conf_path}.")
        conf_file = conf_path
    elif not default_file.is_file():
        raise FileNotFoundError(f"Konfigurationsfilen findes ikke her: {default_file}.")
    else:
        conf_file = default_file

    with open(conf_file) as c:
        try:
            config: dict = json.load(c)
        except ValueError as e:
            raise ValueError(f"FEJL. Konfigurationsfilen kan ikke parses korrekt: {e}")

        for key in REQUIRED_CONFIG_KEYS:
            if key not in config:
                raise ValueError(
                    f"FEJL. Mangler følgende påkrævede konfigurationsnøgle: {key}"
                )
            os.environ["AFLEVERING_" + key.upper()] = config[key]

            # for k, v in config.items():
            #     if k.lower() in REQUIRED_CONFIG_KEYS:
            #         os.environ[k.upper()] = str(v)
