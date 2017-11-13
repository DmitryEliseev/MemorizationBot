#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Работа с БД
"""

import os
import datetime

from peewee import Model
from peewee import SqliteDatabase
from peewee import CharField
from peewee import DateField
from peewee import BigIntegerField
from peewee import ForeignKeyField

from config import SETTINGS

from notification_model import RemindingModel
from notification_model import get_all_dates_for_notification

# path_to_db = SETTINGS.PATH_TO_DB_LOCAL
path_to_db = SETTINGS.PATH_TO_DB_SERVER

_database = SqliteDatabase(path_to_db)


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


def get_all_notifications():
    if not _is_inited:
        _init_db()

    notifications = []

    for date, notification_type in get_all_dates_for_notification():
        remindings = Reminding.select().where((Reminding.memorization_date == date))

        if remindings:
            for reminding in remindings:
                notifications.append(
                    RemindingModel(
                        reminding.caption,
                        reminding.year,
                        reminding.link,
                        reminding.author.name,
                        reminding.author.birthday,
                        reminding.author.death_day,
                        reminding.memorization_date,
                        notification_type
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


def full_db():
    # Чтение данных из файла
    with open('reminding.db.sql', 'r', encoding="utf-8") as file:
        insert_commands = file.read().split(';')[1:-2]

    # Построчное исполнение команд
    for insert in insert_commands:
        _database.execute_sql(insert)


def _init_db():
    """
    Создаёт таблицы, если ещё не были созданы
    """

    global _is_inited
    _database.connect()
    _database.create_tables([Author, Reminding], safe=True)
    print("БД создана")
    full_db()
    print("БД наполнена")
    _is_inited = True


if os.path.isfile(path_to_db):
    _is_inited = True
else:
    _is_inited = False
