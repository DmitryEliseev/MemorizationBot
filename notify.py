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
from database import get_today_notifications
from database import get_week_notifications
import logs_helper

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(SETTINGS.TOKEN)


def send_notifications():
    notifications = get_today_notifications()

    if notifications:
        for notification in notifications:
            bot.send_message(
                SETTINGS.TELEGRAM.OWNER_ID,
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

    notifications = get_week_notifications()

    if notifications:
        bot.send_message(
            SETTINGS.TELEGRAM.OWNER_ID,
            '\n\n'.join([str(n) for n in notifications])
        )
    else:
        bot.send_message(
            SETTINGS.TELEGRAM.OWNER_ID,
            "На этой неделе нет плановых повторений"
        )


if SETTINGS.TIME_ZONE == "UTC":
    notification_time_list = ["06:00", "20:00"]
else:
    notification_time_list = ["09:00", "23:00"]

# Уведомления о повторениях утром и вечером
schedule.every().day.at(notification_time_list[0]).do(send_notifications)
schedule.every().day.at(notification_time_list[1]).do(send_notifications)

# Уведомление о предстоящих на неделю повторениях
schedule.every().monday.at(notification_time_list[0]).do(send_week_notifications)

while True:
    schedule.run_pending()
    time.sleep(1)
