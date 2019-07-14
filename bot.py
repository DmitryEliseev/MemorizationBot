#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Основная логика
"""

import sys

import logging
import logging.config

from time import sleep

import telebot
from telebot.types import Update

import cherrypy
from cherrypy import request

from database import get_all_poems
from database import get_coming_notifications
from database import add_manual_repetition
from database import insert_author
from database import insert_poem
from database import InsertAuthorException, InsertPoemException, InsertReminder

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

    logger.info('Обработана команда /start')


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

    logger.info('Обработана команда /list')


@bot.message_handler(commands=['detlist'])
def list_all_poems_detailed(message):
    """Все стихотворения с детальной информацией"""

    poems = [poem.author_poem_year_link_date_str() for poem in get_all_poems()]
    bot.send_message(
        message.chat.id,
        '\n\n'.join(poems),
        disable_web_page_preview=True
    )

    logger.info('Обработана команда /detlist')


@bot.message_handler(commands=['nextmonth'])
def list_next_30_days_notifications(message):
    poems = [str(poem) for poem in get_coming_notifications(days=30)]

    if poems:
        bot.send_message(message.chat.id, '\n\n'.join(poems))
    else:
        bot.send_message(message.chat.id, 'Уведомлений на ближайшие 30 дней нет')

    logger.info('Обработана команда /nextmonth')


@bot.message_handler(commands=['addauthor'])
def add_author(message):
    """Добавление автора в БД"""

    msg_text = message.text[len('/addauthor'):]
    try:
        author, date_of_birthday, date_of_death = msg_text.split(';')
        insert_author(author.strip(), date_of_birthday.strip(), date_of_death.strip())
        bot.send_message(message.chat.id, constants.MSG_SUCCESS_AUTHOR_INSERT)
        logger.info('Успешно выполнена команда /addauthor')
    except ValueError:
        bot.send_message(
            message.chat.id,
            constants.ERROR_WRONG_ADD_AUTHOR_FORMAT
        )

        logger.info(
            'При выполнении команды /addauthor был несоблюден формат '
            'ввода данных. Текст сообщения: {}'.format(constants.ERROR_WRONG_ADD_AUTHOR_FORMAT, message.text)
        )
    except InsertAuthorException as e:
        bot.send_message(message.chat.id, e)

        logger.error('При выполнении команды /addauthor возникла ошибка: {}'.format(e))


@bot.message_handler(commands=['addpoem'])
def add_poem(message):
    """Добавление стихотворения в БД"""

    msg_text = message.text[len('/addpoem'):]
    try:
        surname, caption, year, link = msg_text.split(';')
        insert_poem(surname.strip(), caption.strip(), year.strip(), link.strip())
        bot.send_message(message.chat.id, constants.MSG_SUCCESS_POEM_INSERT)
        logger.info('Успешно выполнена команда /addpoem')
    except ValueError:
        bot.send_message(
            message.chat.id,
            constants.ERROR_WRONG_ADD_POEM_FORMAT
        )

        logger.info(
            'При выполнении команды /addpoem был несоблюден формат '
            'ввода данных. Текст сообщения: {}'.format(constants.ERROR_WRONG_ADD_POEM_FORMAT, message.text)
        )
    except InsertPoemException as e:
        bot.send_message(message.chat.id, e)
        logger.error('При выполнении команды /addauthor возникла ошибка: {}'.format(e))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Обработка inline-кнопок"""

    poem_id = int(call.data.split('_')[1])

    if call.data.startswith('done'):
        bot.send_message(call.message.chat.id, 'Спасибо, что повторили стихотворение #{}'.format(poem_id))
        logger.info('Стихотворение ID:{} повторено!'.format(poem_id))
        # TODO: хранить статистику в БД
    elif call.data.startswith('rep'):
        try:
            add_manual_repetition(poem_id)
            bot.send_message(
                call.message.chat.id,
                'Стихотворение #{} сохранено для дополнительного повторения'.format(poem_id)
            )
            logger.info('Стихотворение ID:{} сохранено для дополнительных повторений!'.format(poem_id))
        except InsertReminder as ex1:
            bot.send_message(call.message.chat.id, ex1)
            logger.info('Стихотворение ID:{}. {}'.format(poem_id, ex1))
        except Exception as ex2:
            bot.send_message(call.message.chat.id, "Что-то пошло не так")
            logger.error('Стихотворение ID:{}. {}'.format(poem_id, ex2))


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

            logger.info('Бот запущен. Режим: webhook. Попытка {}'.format(attempt))
        else:
            msg = '❌ Бот прекратил работу'
            notify_admin(msg)
            logger.info(msg)
    except:
        sleep(2)
        start_webhook_server(WEBHOOK_URL_PATH, attempt=attempt + 1)
    finally:
        final_msg = 'Файл bot.py прекратил исполнение'
        logger.error(final_msg)
        notify_admin("❌ Бот выключен")


def start_bot():
    """Запуск бота"""

    if int(SETTINGS['test_mode']):
        # Работа на пуллинге локально
        bot.remove_webhook()

        # Сообщение о том, что бот запущен
        notify_admin('Бот запущен')
        logger.info('Бот запущен. Режим: polling')

        while True:
            try:
                bot.polling(none_stop=True, interval=0, timeout=0)
            except Exception as ex:
                logger.error(ex)
                sleep(10)
            finally:
                final_msg = 'Файл bot.py прекратил исполнение'
                logger.error(final_msg)
                notify_admin("❌ Бот выключен")
                sys.exit(0)
    else:
        WEBHOOK_HOST = SETTINGS['webhook_host']
        WEBHOOK_PORT = int(SETTINGS['webhook_port'])
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

        logger.info('Вебхук успешно установлен: {}'.format(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH))

        # Настройки сервера CherryPy
        cherrypy.config.update({
            'server.socket_host': WEBHOOK_LISTEN,
            'server.socket_port': WEBHOOK_PORT,
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': WEBHOOK_SSL_CERT,
            'server.ssl_private_key': WEBHOOK_SSL_PRIV
        })

        logger.info('Конфигурация CherryPy обновлена')

        start_webhook_server(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
