#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Файл для считывания конфигурации
"""

import configparser
_config = configparser.ConfigParser()
_config.read('settings.ini')

SETTINGS = {}

_cur_settings = _config['current_settings']['profile']
for key in _config[_cur_settings].keys():
    SETTINGS[key] = _config[_cur_settings][key]

for key in _config['default']:
    if key not in SETTINGS.keys():
        SETTINGS[key] = _config['default'][key]
