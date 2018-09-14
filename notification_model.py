#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Модель напоминаний
"""

import datetime
import dateutil.relativedelta as datedelta

# Модель напоминаний
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


def get_all_dates_for_notification(days=None):
    """Список дат для уведомлений"""

    dates_for_notification = {}
    now = datetime.datetime.now().date()

    # Предстоящие уведомления на N дней

    if days:
        for i in range(days):
            starting_point = now + datedelta.relativedelta(days=i)
            for model in repeat_model:
                notification_date, message = model(starting_point)
                dates_for_notification[notification_date] = message
    # Уведомления на текущий год
    else:
        for model in repeat_model:
            notification_date, message = model(now)
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
        return '{} {}.{}.'.format(surname, name[0], second_name[0])

    def format_memo_date(self):
        return self.memo_date.strftime('%d.%m.%Y')

    def __str__(self):
        str_model = (
            '{author_name} ({birthday}-{death_day}). '
            '{caption} ({year}). Выучено {memo_date}, '
            'повторение {notification_type}. {link}'
        )

        return str_model.format(
            caption=self.caption,
            year=self.year,
            link=self.link,
            author_name=self.short_author_name(),
            birthday=self.author_birthday,
            death_day=self.author_death_day,
            memo_date=self.format_memo_date(),
            notification_type=self.notification_type
        )

    def short_str(self):
        str_model = (
            '{author_name} ({birthday}-{death_day}) - '
            '{caption} ({year}). Выучено {memo_date}. {link}'
        )

        return str_model.format(
            caption=self.caption,
            year=self.year,
            link=self.link,
            author_name=self.short_author_name(),
            birthday=self.author_birthday,
            death_day=self.author_death_day,
            memo_date=self.format_memo_date(),
        )

    def author_poem_name_str(self):
        return '{} {}'.format(self.short_author_name(), self.caption)

    def author_poem_year_link_date_str(self):
        str_model = '{} {} ({}). Выучено {}. {}'
        return str_model.format(
            self.short_author_name(),
            self.caption,
            self.year,
            self.format_memo_date(),
            self.link
        )
