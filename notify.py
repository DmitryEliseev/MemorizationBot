#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Обработчик уведомлений о повторении
"""

import time
import datetime
import schedule
import telebot
import json

from database import get_coming_notifications
from bot import notify_admin

import logging
import logging.config

from config import SETTINGS

logging.config.fileConfig('log_config.ini')
logger = logging.getLogger('myLogger')
telebot.logger.setLevel(logging.DEBUG)

TG_TOKEN = SETTINGS['telegram_token']
tg_admin_id = SETTINGS['telegram_admin_id']

bot = telebot.TeleBot(TG_TOKEN)


def keyboard_for_notification(notif):
    buttons = [
        {
            'text': '✅',
            'callback_data': 'done_{}'.format(notif.id)
        },
        {
            'text': '🔄',
            'callback_data': 'rep_{}'.format(notif.id)
        }
    ]

    return json.dumps({'inline_keyboard': [buttons]})


def send_notifications():
    notifications = get_coming_notifications()

    if notifications:
        message = '#повторение_дня\n{}'

        for notification in notifications:
            bot.send_message(
                tg_admin_id,
                message.format(str(notification)),
                reply_markup=keyboard_for_notification(notification),
                disable_web_page_preview=True
            )

        logger.info('Отправлены повторения дня')
    else:
        logger.info('Повторений на день нет')


def send_week_notifications():
    """
    Уведомление о предстояющих на неделю повторениях
    """

    notifications = get_coming_notifications(days=7)

    if notifications:
        message = (
            '#превью_недели\n{}'.format(
                '\n\n'.join([n.short_str() for n in notifications])
            )
        )

        bot.send_message(
            tg_admin_id,
            message,
            disable_web_page_preview=True
        )
        logger.info('Отправлены повторения на предстояющую неделю')
    else:
        msg = 'На предстояющей неделе нет повторений'
        bot.send_message(tg_admin_id, msg)
        logger.info(msg)


def notification():
    try:
        if int(SETTINGS['test_mode']):
            # Тестовый режим
            now = datetime.datetime.now()
            in_one_minute = now + datetime.timedelta(minutes=1)
            time_for_schedule = '{}:{}'.format(in_one_minute.hour, in_one_minute.minute)

            schedule.every().day.at(time_for_schedule).do(send_notifications)
            schedule.every().day.at(time_for_schedule).do(send_week_notifications)
        else:
            # Production: уведомления о повторениях утром и вечером
            schedule.every().day.at("04:00").do(send_notifications)
            schedule.every().day.at("19:00").do(send_notifications)
            schedule.every().monday.at("04:00").do(send_week_notifications)

        notify_admin("Ежедневные уведомления включены")
        logger.info('Файл notify.py запущен')

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as ex:
        logger.error("Произошла ошибка: {}".format(repr(ex)))
    finally:
        final_msg = 'Файл notify.py прекратил исполнение'
        logger.error(final_msg)
        notify_admin("❌ Ежедневные уведомления отключены")


if __name__ == '__main__':
    notification()
