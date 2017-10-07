import json


class SettingStorer:
    def __init__(self, in_dict):
        for key in in_dict:
            value = in_dict.get(key)
            if isinstance(value, dict):
                value = SettingStorer(value)
            setattr(self, key, value)


with open('settings.json', 'r', encoding='utf-8') as file:
    _settings_data = json.loads(file.read())

SETTINGS = SettingStorer(_settings_data)
