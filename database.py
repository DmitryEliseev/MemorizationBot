#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Работа с БД
"""

from peewee import Model, SqliteDatabase, CharField, DateField, BigIntegerField, ForeignKeyField
import datetime

from config import SETTINGS

from model import RemindingModel
from model import get_all_dates_for_notification

_database = SqliteDatabase(SETTINGS.PATH_TO_DB)


class Reminding(Model):
    user_id = BigIntegerField()
    memorization_date = DateField()
    year = BigIntegerField(null=True)
    caption = CharField()
    link = CharField(null=True)
    author = ForeignKeyField(Author)

    class Meta:
        database = _database


class Author(Model):
    name = CharField()
    birthday = BigIntegerField()
    deathday = BigIntegerField()

    class Meta:
        database = _database


def get_all_notifications(user_id):
    if not _is_inited:
        _init_db()

    notifications = []

    for date in get_all_dates_for_notification():
        remindings = Reminding.select().where(
            (Reminding.memorization_date == date) & (Reminding.user_id == user_id)
        )
        if remindings:
            for reminding in remindings:
                notifications.append(
                    RemindingModel(
                        reminding.caption,
                        reminding.link
                    )

                )

    return notifications


def get_all_users_id():
    if not _is_inited:
        _init_db()

    users_id = []
    for user_id in Reminding.select(Reminding.user_id).distinct():
        users_id.append(user_id)

    return users_id


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
    with open('reminding.sql', 'r', encoding="utf-8") as file:
        inserts = file.read().split(';')[1:-2]

    # Построчное исполнение команд
    for i in inserts:
        _database.execute_sql(i)


def _init_db():
    """
    Создаёт таблицы, если ещё не были созданы
    """
    global _is_inited
    _database.connect()
    _database.create_table(Reminding, safe=True)
    full_db()
    _is_inited = True


_is_inited = False
