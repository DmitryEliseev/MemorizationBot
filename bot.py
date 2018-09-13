#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Основная логика
"""

import logging
import telebot

from config import config
import constants
import logs_helper

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

tg_token = config['telegram_token']
tg_admin_id = config['telegram_admin_id']
bot = telebot.TeleBot(tg_token)


@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id,
        constants.MSG_START_COMMAND
    )


@bot.message_handler(commands=['list'])
def list_msg(message):
    """Все стихотворения"""
    pass


@bot.message_handler(commands=['detlist'])
def list_msg(message):
    """Все стихотворения с детальной информацией"""
    pass


if __name__ == '__main__':
    bot.send_message(tg_admin_id, "Бот запущен")
