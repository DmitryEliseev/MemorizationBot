#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Основная логика
"""

import logging
import logging.config

from time import sleep

import telebot
from telebot.types import Update

import cherrypy
from cherrypy import request

from database import get_all_poems
from database import get_coming_notifications
from database import insert_author
from database import insert_poem
from database import InsertAuthorException, InsertPoemException

from config import SETTINGS
import constants

logging.config.fileConfig('log_config.ini')
logger = logging.getLogger('myLogger')

TG_TOKEN = SETTINGS['telegram_token']
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(TG_TOKEN)


@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id,
        constants.MSG_START_COMMAND
    )


@bot.message_handler(commands=['list'])
def list_all_poems(message):
    """Все стихотворения"""

    poems = [
        '{}. {}'.format(idx + 1, poem.author_poem_name_str())
        for idx, poem in enumerate(get_all_poems())
    ]
    bot.send_message(
        message.chat.id,
        '\n'.join(poems)
    )


@bot.message_handler(commands=['detlist'])
def list_all_poems_detailed(message):
    """Все стихотворения с детальной информацией"""

    poems = [poem.author_poem_year_link_date_str() for poem in get_all_poems()]
    bot.send_message(
        message.chat.id,
        '\n\n'.join(poems),
        disable_web_page_preview=True
    )


@bot.message_handler(commands=['nextmonth'])
def list_next_30_days_notifications(message):
    poems = [str(poem) for poem in get_coming_notifications(days=30)]

    if poems:
        bot.send_message(message.chat.id, '\n\n'.join(poems))
    else:
        bot.send_message(message.chat.id, 'Уведомлений на ближайшие 30 дней нет')


@bot.message_handler(commands=['addauthor'])
def add_author(message):
    """Добавление автора в БД"""

    msg_text = message.text[len('/addauthor'):]
    try:
        author, date_of_birthday, date_of_death = msg_text.split(';')
        insert_author(author.strip(), date_of_birthday.strip(), date_of_death.strip())
        bot.send_message(message.chat.id, constants.MSG_SUCCESS_AUTHOR_INSERT)
    except ValueError:
        bot.send_message(
            message.chat.id,
            constants.ERROR_WRONG_ADD_AUTHOR_FORMAT
        )
    except InsertAuthorException as e:
        bot.send_message(message.chat.id, e)


@bot.message_handler(commands=['addpoem'])
def add_poem(message):
    """Добавление стихотворения в БД"""

    msg_text = message.text[len('/addpoem'):]
    try:
        surname, caption, year, link = msg_text.split(';')
        insert_poem(surname.strip(), caption.strip(), year.strip(), link.strip())
        bot.send_message(message.chat.id, constants.MSG_SUCCESS_POEM_INSERT)
    except ValueError:
        bot.send_message(
            message.chat.id,
            constants.ERROR_WRONG_ADD_POEM_FORMAT
        )
    except InsertPoemException as e:
        bot.send_message(message.chat.id, e)


def notify_admin(message):
    """Уведомления админа"""

    bot.send_message(SETTINGS['telegram_admin_id'], message)


class WebhookServer:
    """Класс для CherryPy приложения"""

    @cherrypy.expose
    def index(self):
        if request.headers.get('content-type', None) == 'application/json':
            length = int(request.headers['content-length'])
            json_string = request.body.read(length).decode("utf-8")
            update = Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


def start_webhook_server(WEBHOOK_URL_PATH, attempt=0):
    """Запуск и перезапуск сервера при необходимости"""

    try:
        if attempt <= 5:
            # Запуск сервера
            cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

            # Сообщение о том, что бот запущен
            msg = 'запущен' if not attempt else 'перезапущен в {} раз'.format(attempt)
            notify_admin("Бот {} (webhook)".format(msg))
        else:
            notify_admin("Бот упал")
    except:
        sleep(10)
        start_webhook_server(WEBHOOK_URL_PATH, attempt=attempt + 1)


def start_bot():
    """Запуск бота"""

    if SETTINGS['test_mode']:
        # Работа на пуллинге локально
        bot.remove_webhook()

        # Сообщение о том, что бот запущен
        notify_admin("Бот запущен (polling)")

        bot.polling(none_stop=True)
    else:
        WEBHOOK_HOST = SETTINGS['webhook_host']
        WEBHOOK_PORT = SETTINGS['webhook_port']
        WEBHOOK_LISTEN = SETTINGS['webhook_listen']

        WEBHOOK_SSL_CERT = './webhook_cert.pem'
        WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

        WEBHOOK_URL_BASE = 'https://{}:{}'.format(WEBHOOK_HOST, WEBHOOK_PORT)
        WEBHOOK_URL_PATH = '/{}/'.format(TG_TOKEN)

        # Удаление и создание вебхука
        bot.remove_webhook()
        bot.set_webhook(
            url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
            certificate=open(WEBHOOK_SSL_CERT, 'r')
        )

        # Настройки сервера CherryPy
        cherrypy.config.update({
            'server.socket_host': WEBHOOK_LISTEN,
            'server.socket_port': WEBHOOK_PORT,
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': WEBHOOK_SSL_CERT,
            'server.ssl_private_key': WEBHOOK_SSL_PRIV
        })

        start_webhook_server(WEBHOOK_URL_PATH)


if __name__ == '__main__':
    start_bot()
