from src.constants import SETTINGS_FILE_PATH
from src.settings_parser import SettingsParser

SETTINGS = SettingsParser.load_settings_from_toml(path=SETTINGS_FILE_PATH)
