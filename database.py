#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Работа с БД
"""

import os
import datetime
import logging

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


class Repetition(Model):
    poem = ForeignKeyField(Reminding, related_name='poem')
    repetition_date = DateField()

    class Meta:
        database = _database


def init_db(func):
    def wrapper(*args, **kwargs):
        if not _is_inited:
            _init_db()

        result = func(*args, **kwargs)
        return result

    return wrapper


@init_db
def get_coming_notifications(days=None):
    """Уведомления на сегодня"""

    dates_for_notification = get_all_dates_for_notification(days=days)

    reminding_list = (
        Reminding
            .select()
            .where((Reminding.memorization_date << list(dates_for_notification.keys())))
    )

    notifications = []
    for reminding in reminding_list:
        notifications.append(
            RemindingModel(
                reminding.id,
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


class InsertPoemException(Exception):
    pass


class InsertAuthorException(Exception):
    pass


class InsertReminder(Exception):
    pass


def add_insert_to_sql(table, *args):
    """Дублирование создания сущности в SQL файле"""

    output_str = "INSERT INTO `{}` VALUES ({},{});\n"

    content = []
    with open('reminding.db.sql', 'r', encoding="utf-8") as file:
        content = file.readlines()

    author_inserts = sum(1 for row in content if 'author' in row)
    remindings_inserts = len(content) - author_inserts - 2

    index_to_insert = author_inserts if table == 'author' else author_inserts + remindings_inserts
    right_part = content[index_to_insert].split('(')[1]
    id_to_insert = int(right_part.split(',')[0])

    content.insert(
        index_to_insert + 1,
        output_str.format(
            table,
            id_to_insert + 1,
            ','.join(map(str, args))
        )
    )

    with open('reminding.db.sql', 'w', encoding="utf-8") as file:
        file.write(''.join(content))


@init_db
def check_author_existence(author_surname):
    """Проверка на наличие автора в БД"""

    for author in Author.select():
        if author_surname.lower() == author.name.split()[0].lower():
            return author


@init_db
def check_poem_existence(caption):
    """Проверка на наличие стихотворения в БД"""

    try:
        Reminding.get(Reminding.caption == caption)
        return True
    except:
        return False


@init_db
def insert_poem(author_surname, caption, year, link):
    """Занесенив в БД стихотворения"""

    author = check_author_existence(author_surname)
    if not author:
        raise InsertPoemException('Не найден автор. Воспользуйтесь командой /addauthor')

    if check_poem_existence(caption):
        raise InsertPoemException('Такое стихотворение уже есть')

    try:
        int(year)
    except ValueError:
        raise InsertPoemException('Неверный тип года написания стихотворения')

    current_date = datetime.datetime.now().date()
    Reminding.create(
        author=author,
        memorization_date=current_date,
        year=int(year),
        caption=caption,
        link=link
    )

    add_insert_to_sql(
        'reminding',
        "'{}'".format(current_date.strftime("%Y-%m-%d")),
        author.id,
        year,
        "'{}'".format(caption),
        "'{}'".format(link)
    )


@init_db
def insert_author(author_fio, year_of_birthday, year_of_death):
    """Занесение в БД автора"""

    author_surname = author_fio.split()[0].strip()
    if check_author_existence(author_surname):
        raise InsertAuthorException('Данный автор уже есть в базе данных')

    try:
        int(year_of_birthday)
    except ValueError:
        raise InsertAuthorException('Неверный тип года рождения')

    try:
        int(year_of_death)
    except ValueError:
        raise InsertAuthorException('Неверный тип года смерти')

    Author.create(
        name=author_fio,
        birthday=int(year_of_birthday),
        death_day=int(year_of_death)
    )

    add_insert_to_sql(
        'author',
        "'{}'".format(author_fio),
        year_of_birthday,
        year_of_death
    )


@init_db
def get_all_poems():
    notifications = []
    for reminding in Reminding.select():
        notifications.append(
            RemindingModel(
                reminding.id,
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


@init_db
def add_manual_repetition(poem_id: int):
    poem = Reminding.get(Reminding.id == poem_id)
    reps = Repetition.select().where(Repetition.poem_id == poem_id)
    if reps:
        raise InsertReminder('Дополнительное повторение стихотворения #{} уже сохранено'.format(poem_id))

    Repetition.create(poem=poem, repetition_date=datetime.datetime.now().date())

@init_db
def get_coming_manual_notifications(days):
    """Получение повторений, который были настроены дополнительно"""

    dates_for_notification = get_all_dates_for_notification(days=days)

    repetition_list = (
        Repetition
            .select()
            .where((Repetition.repetition_date << list(dates_for_notification.keys())))
    )

    notifications = []
    for repetition in repetition_list:
        reminding = repetition.poem

        notifications.append(
            RemindingModel(
                reminding.id,
                reminding.caption,
                reminding.year,
                reminding.link,
                reminding.author.name,
                reminding.author.birthday,
                reminding.author.death_day,
                reminding.memorization_date,
                dates_for_notification[repetition.repetition_date]
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
    _database.create_tables([Author, Reminding, Repetition], safe=True)
    logger.info("БД создана")
    full_db()
    logger.info("БД наполнена")
    _is_inited = True


if os.path.isfile(PATH_TO_DB):
    _is_inited = True
else:
    _is_inited = False
