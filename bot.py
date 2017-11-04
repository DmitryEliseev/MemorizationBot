#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Основная логика
"""

import logging
import telebot
from config import SETTINGS
import constants

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(SETTINGS.TOKEN)


@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id,
        constants.MSG_START_COMMAND
    )


if __name__ == '__main__':
    bot.send_message(SETTINGS.TELEGRAM_OWNER_ID, "Бот запущен")
    bot.polling(none_stop=True)
