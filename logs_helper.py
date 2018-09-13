#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Логгирование
"""

import sys
import logging
from config import config


def init_logging():
    """
    Устанавливает обработчики логгирования и другая инициализация логгирования
    """

    datetime_format = "{} {}".format("%Y.%m.%d", "%H:%M:%S")

    if init_logging.is_inited:
        logging.warning("Вызываем init_logging повторно. Что-то не так")
        return

    init_logging.is_inited = True
    logger = logging.getLogger()  # RootLogger
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(config['path_to_log'], 'a', 'utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s  %(funcName)s at %(module)s:%(lineno)d %(message)s',
        datefmt=datetime_format
    ))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt=datetime_format
    ))
    logger.addHandler(console_handler)


init_logging.is_inited = False
init_logging()