#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Работа с БД
"""

import os
import datetime
import logging
import logging.config

from peewee import Model
from peewee import SqliteDatabase
from peewee import CharField, DateField, BigIntegerField
from peewee import ForeignKeyField

from config import SETTINGS

from notification_model import RemindingModel
from notification_model import get_all_dates_for_notification

logging.config.fileConfig('log_config.ini')
logger = logging.getLogger('myLogger')

PATH_TO_DB = SETTINGS['path_to_db']
_database = SqliteDatabase(PATH_TO_DB)


class Author(Model):
    name = CharField()
    birthday = BigIntegerField()
    death_day = BigIntegerField()

    class Meta:
        database = _database


class Reminding(Model):
    memorization_date = DateField()
    author = ForeignKeyField(Author, related_name='author')
    year = BigIntegerField(null=True)
    caption = CharField()
    link = CharField()

    class Meta:
        database = _database


def get_coming_notifications(days=None):
    """Уведомления на сегодня"""

    if not _is_inited:
        _init_db()

    notifications = []

    dates_for_notification = get_all_dates_for_notification(days=days)

    reminding_list = (
        Reminding
            .select()
            .where((Reminding.memorization_date << list(dates_for_notification.keys())))
    )

    for reminding in reminding_list:
        notifications.append(
            RemindingModel(
                reminding.caption,
                reminding.year,
                reminding.link,
                reminding.author.name,
                reminding.author.birthday,
                reminding.author.death_day,
                reminding.memorization_date,
                dates_for_notification[reminding.memorization_date]
            )

        )

    return notifications


def insert_notification(user_id, caption, link=None):
    if not _is_inited:
        _init_db()

    Reminding.create(
        user_id=user_id,
        memorization_date=datetime.datetime.now().date(),
        caption=caption,
        link=link
    )


def get_all_poems():
    if not _is_inited:
        _init_db()

    notifications = []
    for reminding in Reminding.select():
        notifications.append(
            RemindingModel(
                reminding.caption,
                reminding.year,
                reminding.link,
                reminding.author.name,
                reminding.author.birthday,
                reminding.author.death_day,
                reminding.memorization_date,
                reminding.memorization_date
            )
        )
    return notifications


def full_db():
    """Заполнение БД"""

    # Чтение данных из файла
    with open('reminding.db.sql', 'r', encoding="utf-8") as file:
        insert_commands = file.read().split(';')[1:-2]

    # Построчное исполнение команд
    for insert in insert_commands:
        _database.execute_sql(insert)


def _init_db():
    """Создание БД, если ее нет"""

    global _is_inited
    _database.connect()
    _database.create_tables([Author, Reminding], safe=True)
    logger.info("БД создана")
    full_db()
    logger.info("БД наполнена")
    _is_inited = True


if os.path.isfile(PATH_TO_DB):
    _is_inited = True
else:
    _is_inited = False
