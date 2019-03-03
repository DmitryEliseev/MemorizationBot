#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Обработчик уведомлений о повторении
"""

import time
import schedule
import telebot

from database import get_coming_notifications
from bot import notify_admin

import logging
import logging.config

from config import SETTINGS

logging.config.fileConfig('log_config.ini')
logger = logging.getLogger('myLogger')
telebot.logger.setLevel(logging.DEBUG)

tg_token = SETTINGS['telegram_token']
tg_admin_id = SETTINGS['telegram_admin_id']

bot = telebot.TeleBot(tg_token)


def send_notifications():
    notifications = get_coming_notifications()

    if notifications:
        message = (
            '*Повторения на сегодня* #повторение\_дня\n{}'.format(
                '\n\n'.join([str(n) for n in notifications])
            )
        )

        bot.send_message(
            tg_admin_id,
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )


def send_week_notifications():
    """
    Уведомление о предстояющих на неделю повторениях
    """

    notifications = get_coming_notifications(days=7)

    if notifications:
        message = (
            '*Повторения на наделю* #превью\_недели\n{}'.format(
                '\n\n'.join([n.short_str() for n in notifications])
            )
        )

        bot.send_message(
            tg_admin_id,
            message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    else:
        bot.send_message(
            tg_admin_id,
            "На этой неделе нет плановых повторений"
        )


def notification():
    try:
        # Уведомления о повторениях утром и вечером
        schedule.every().day.at("04:00").do(send_notifications)
        schedule.every().day.at("19:00").do(send_notifications)

        schedule.every().monday.at("04:00").do(send_week_notifications)

        notify_admin("Ежедневные уведомления включены")

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as ex:
        logging.error("Произошла ошибка: {}".format(repr(ex)))
        raise ex
    finally:
        final_msg = "Бот прекратил свою работу"
        logging.error(final_msg)
        notify_admin(final_msg)


if __name__ == '__main__':
    notification()
