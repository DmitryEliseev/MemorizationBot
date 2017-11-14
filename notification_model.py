#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Модель напоминаний
"""

import datetime
import dateutil.relativedelta as datedelta

# Модель напоминаний без сдвига по дате
repeat_model_without_shift = (
    lambda a: {a - datedelta.relativedelta(days=1): 'через день'},
    lambda a: {a - datedelta.relativedelta(days=2): 'через 2 дня'},
    lambda a: {a - datedelta.relativedelta(days=4): 'через 4 дня'},
    lambda a: {a - datedelta.relativedelta(weeks=1): 'через неделю'},
    lambda a: {a - datedelta.relativedelta(weeks=2): 'через 2 недели'},
    lambda a: {a - datedelta.relativedelta(months=1): 'через месяц'},
    lambda a: {a - datedelta.relativedelta(months=2): 'через 2 месяца'},
    lambda a: {a - datedelta.relativedelta(months=6): 'через 6 месяцев'},
    lambda a: {a - datedelta.relativedelta(years=1): 'через год'},
    lambda a: {a - datedelta.relativedelta(years=2): 'через 2 года'}
)

# Тестовая модель напоминаний: напоминания каждый день
# в течение месяца после запоминания
test_repeat_model = [lambda a: a - datedelta.relativedelta(days=i) for i in range(32)]

repeat_model = repeat_model_without_shift


def get_all_dates_for_notification():
    """Список дат для уведомления в текущий день"""
    dates_for_notification = []

    now = datetime.datetime.now().date()

    for model in repeat_model:
        dates_for_notification.append(model(now))

    return dates_for_notification


def get_all_dates_for_week_notification():
    """Список дат для уведомления на неделю вперед"""
    dates_for_notification = []

    for i in range(7):
        now = datetime.datetime.now().date()
        starting_point = now + datedelta.relativedelta(days=i)
        for model in repeat_model:
            dates_for_notification.append(model(starting_point))

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

    def __str__(self):
        str_model = (
            'Стихотворение: {caption} ({year})\n'
            'Ссылка: {link}\n'
            'Автор: {author_name} ({birthday} - {death_day})\n'
            'Дата запоминания: {memo_date}\n'
            'Стадия повторения: *{notification_type}* после запоминания'
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
