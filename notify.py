#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Обработчик уведомлений о повторении
"""

import logging
import schedule
import telebot

import time
import datetime
import dateutil.relativedelta as datedelta

from config import SETTINGS
from database import get_today_notifications
from database import get_week_notifications
import logs_helper

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(SETTINGS.TELEGRAM.TOKEN)


def send_notifications(second_time=False):
    notifications = get_today_notifications()

    if notifications:
        message = (
            '*Повторения на сегодня* #повторение\_дня\n{}'.format(
                '\n\n'.join([str(n) for n in notifications])
            )
        )

        bot.send_message(
            SETTINGS.TELEGRAM.OWNER_ID,
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    else:
        # Если повторений нет, то не уведомлять об этом второй раз
        if not second_time:
            bot.send_message(
                SETTINGS.TELEGRAM.OWNER_ID,
                "На сегодня уведомлений нет"
            )


def send_week_notifications():
    """
    Уведомление о предстояющих на неделю повторениях
    """

    notifications = get_week_notifications()

    if notifications:
        message = (
            '*Повторения на наделю* #превью\_недели\n{}'.format(
                '\n\n'.join([n.short_str() for n in notifications])
            )
        )

        bot.send_message(
            SETTINGS.TELEGRAM.OWNER_ID,
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    else:
        bot.send_message(
            SETTINGS.TELEGRAM.OWNER_ID,
            "На этой неделе нет плановых повторений"
        )


def test_notification_time():
    cur_datetime = datetime.datetime.now()
    soon1 = cur_datetime + datedelta.relativedelta(minutes=1)
    soon2 = cur_datetime + datedelta.relativedelta(minutes=2)

    return [datetime.datetime.strftime(t, '%H:%M') for t in [soon1, soon2]]


if SETTINGS.TEST_MODE:
    notification_time_list = test_notification_time()
else:
    if SETTINGS.TIME_ZONE == "UTC":
        notification_time_list = ["06:00", "20:00"]
    else:
        notification_time_list = ["09:00", "23:00"]

try:
    # Уведомления о повторениях утром и вечером
    schedule.every().day.at(notification_time_list[0]).do(send_notifications)
    schedule.every().day.at(notification_time_list[1]).do(send_notifications, second_time=True)

    # Уведомление о предстоящих на неделю повторениях
    if SETTINGS.TEST_MODE:
        current_weekday = datetime.datetime.now().weekday()
        if current_weekday == 0:
            schedule.every().monday.at(notification_time_list[0]).do(send_week_notifications)
        elif current_weekday == 1:
            schedule.every().tuesday.at(notification_time_list[0]).do(send_week_notifications)
        elif current_weekday == 2:
            schedule.every().wednesday.at(notification_time_list[0]).do(send_week_notifications)
        elif current_weekday == 3:
            schedule.every().thursday.at(notification_time_list[0]).do(send_week_notifications)
        elif current_weekday == 4:
            schedule.every().friday.at(notification_time_list[0]).do(send_week_notifications)
        elif current_weekday == 5:
            schedule.every().saturday.at(notification_time_list[0]).do(send_week_notifications)
        else:
            schedule.every().sunday.at(notification_time_list[0]).do(send_week_notifications)
    else:
        schedule.every().monday.at(notification_time_list[0]).do(send_week_notifications)

    bot.send_message(SETTINGS.TELEGRAM.OWNER_ID, "Бот запущен")

    while True:
        schedule.run_pending()
        time.sleep(1)
except Exception as ex:
    logging.error("Произошла ошибка: {}".format(repr(ex)))
    raise ex
finally:
    final_msg = "Бот прекратил свою работу"
    logging.info(final_msg)
    bot.send_message(SETTINGS.TELEGRAM.OWNER_ID, final_msg)
