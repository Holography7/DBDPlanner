from src.constants import SETTINGS_FILE_PATH
from src.schemas import Settings
from src.settings_parser import SettingsParser

SETTINGS: Settings

if not SETTINGS_FILE_PATH.exists():
    from src.utils import is_ran_by_pytest

    is_ran_by_pytest()

    from pathlib import Path

    from src.utils import correct_path, correct_paths

    settings_path = correct_path(initial=str(SETTINGS_FILE_PATH))
    parsed_toml = SettingsParser.parse_toml(path=Path(settings_path))
    parsed_toml['paths'] = correct_paths(initial=parsed_toml['paths'])
    SETTINGS = SettingsParser.parse_data(parsed_toml)
else:
    SETTINGS = SettingsParser.load_settings_from_toml(path=SETTINGS_FILE_PATH)
