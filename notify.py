#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Обработчик уведомлений о повторении
"""

import logging
import schedule
import telebot
import time

from config import SETTINGS
from database import get_all_notifications

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(SETTINGS.TOKEN)


def send_notifications():
    for notification in get_all_notifications():
        bot.send_message(
            SETTINGS.TELEGRAM_OWNER_ID,
            str(notification)
        )


t_test = "22:27"
t_real = "09:00"
job_time = t_real

schedule.every().day.at(job_time).do(send_notifications)

while True:
    schedule.run_pending()
    time.sleep(1)
