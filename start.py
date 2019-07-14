#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Запуск проекта
"""

import threading
from bot import start_bot
from notify import launch_notifications

thread1 = threading.Thread(target=start_bot)
thread1.start()

thread2 = threading.Thread(target=launch_notifications)
thread2.start()
