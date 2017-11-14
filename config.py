#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Файл для считывания конфигурации
"""

import json


class SettingStorer:
    def __init__(self, in_dict, defaults=None):
        if not defaults:
            defaults = {}
        for key in set(in_dict).union(defaults):
            value = in_dict.get(key, defaults.get(key))
            if isinstance(value, dict):
                value = SettingStorer(value, defaults.get(key))
            setattr(self, key, value)


with open('settings.json', 'r', encoding='utf-8') as file:
    _settings_data = json.loads(file.read())

_cur_settings = _settings_data['settings'][_settings_data['cur_settings']]
_default_settings = _settings_data['settings']['default']

SETTINGS = SettingStorer(_cur_settings, _default_settings)
