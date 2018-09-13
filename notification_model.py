#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Модель напоминаний
"""

import datetime
import dateutil.relativedelta as datedelta

# Модель напоминаний без сдвига по дате
classic_repeat_model = [
    lambda a: (a - datedelta.relativedelta(days=1), 'через день'),
    lambda a: (a - datedelta.relativedelta(days=2), 'через 2 дня'),
    lambda a: (a - datedelta.relativedelta(days=4), 'через 4 дня'),
    lambda a: (a - datedelta.relativedelta(weeks=1), 'через неделю'),
    lambda a: (a - datedelta.relativedelta(weeks=2), 'через 2 недели'),
    lambda a: (a - datedelta.relativedelta(months=1), 'через месяц'),
    lambda a: (a - datedelta.relativedelta(months=2), 'через 2 месяца'),
    lambda a: (a - datedelta.relativedelta(months=6), 'через 6 месяцев'),
    lambda a: (a - datedelta.relativedelta(years=1), 'через год'),
    lambda a: (a - datedelta.relativedelta(years=2), 'через 2 года')
]

repeat_model = classic_repeat_model


def get_all_dates_for_notification():
    """Список дат для уведомления в текущий день"""

    dates_for_notification = {}
    now = datetime.datetime.now().date()

    for model in repeat_model:
        notification_date, message = model(now)
        dates_for_notification[notification_date] = message

    return dates_for_notification


def get_all_dates_for_week_notification():
    """Список дат для уведомления на неделю вперед"""

    dates_for_notification = {}

    for i in range(7):
        now = datetime.datetime.now().date()
        starting_point = now + datedelta.relativedelta(days=i)
        for model in repeat_model:
            notification_date, message = model(starting_point)
            dates_for_notification[notification_date] = message

    return dates_for_notification


class RemindingModel:
    """Класс с моделью данных напоминания"""

    def __init__(
            self, caption, year, link, author_name,
            author_birthday, author_death_day, memo_date,
            notification_type
    ):
        self.caption = caption
        self.year = year
        self.link = link
        self.author_name = author_name
        self.author_birthday = author_birthday
        self.author_death_day = author_death_day
        self.memo_date = memo_date
        self.notification_type = notification_type

    def short_author_name(self):
        full_author_name = self.author_name
        surname, name, second_name = full_author_name.split()
        return '{} {}. {}.'.format(surname, name[0], second_name[0])

    def short_str(self):
        str_model = (
            '{author_name} ({birthday}-{death_day}) - '
            '{caption} ({year}). Выучено {memo_date}. '
            '{link}'
        )

        return str_model.format(
            caption=self.caption,
            year=self.year,
            link=self.link,
            author_name=self.short_author_name(),
            birthday=self.author_birthday,
            death_day=self.author_death_day,
            memo_date=self.memo_date,
        )

    def __str__(self):
        str_model = (
            '{author_name} ({birthday}-{death_day}) - '
            '{caption} ({year}). Выучено {memo_date}. '
            'Повторение {notification_type}. {link}'
        )

        return str_model.format(
            caption=self.caption,
            year=self.year,
            link=self.link,
            author_name=self.author_name,
            birthday=self.author_birthday,
            death_day=self.author_death_day,
            memo_date=self.memo_date,
            notification_type=self.notification_type
        )
