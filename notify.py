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
import logs_helper

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(SETTINGS.TOKEN)


def send_notifications():
    notifications = get_all_notifications()

    if notifications:
        for notification in notifications:
            bot.send_message(
                SETTINGS.TELEGRAM_OWNER_ID,
                str(notification),
                reply_markup='Markdown'
            )
    else:
        bot.send_message(
            SETTINGS.TELEGRAM_OWNER_ID,
            "На сегодня уведомлений нет"
        )


def send_week_notifications():
    """
    Уведомление о предстояющих на неделю повторениях
    """

    bot.send_message(
        SETTINGS.TELEGRAM_OWNER_ID,
        "Уведомление на неделю в разработке"
    )


t_test = ["22:27", ]
# TODO: подумать над локализацией времени для различных машин
# https://stackoverflow.com/questions/13218506/how-to-get-system-timezone-setting-and-pass-it-to-pytz-timezone
t_real = ["06:00", "20:00"]
job_times = t_real

for job_time in job_times:
    schedule.every().day.at(job_time).do(send_notifications)

schedule.every().monday.at(job_times[0]).do(send_week_notifications)

while True:
    schedule.run_pending()
    time.sleep(1)
