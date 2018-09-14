#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Основная логика
"""

import logging
import logging.config
import telebot

from config import SETTINGS
import constants

from database import get_all_poems

logging.config.fileConfig('log_config.ini')
logger = logging.getLogger('myLogger')
telebot.logger.setLevel(logging.DEBUG)

tg_token = SETTINGS['telegram_token']
tg_admin_id = SETTINGS['telegram_admin_id']

bot = telebot.TeleBot(tg_token)


@bot.message_handler(commands=['start'])
def start_msg(message):
    """Стартовой сообщение"""

    bot.send_message(
        message.chat.id,
        constants.MSG_START_COMMAND
    )


@bot.message_handler(commands=['list'])
def list_msg(message):
    """Все стихотворения"""

    poems = [poem.author_poem_name_str() for poem in get_all_poems()]
    bot.send_message(
        message.chat.id,
        '\n'.join(poems)
    )


@bot.message_handler(commands=['detlist'])
def list_msg(message):
    """Все стихотворения с детальной информацией"""

    poems = [poem.author_poem_year_link_date_str() for poem in get_all_poems()]
    bot.send_message(
        message.chat.id,
        '\n'.join(poems)
    )


if __name__ == '__main__':
    bot.send_message(tg_admin_id, "Бот запущен")
