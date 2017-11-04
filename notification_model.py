#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Модель напоминаний
"""

import datetime
from random import randint, choice
import dateutil.relativedelta as datedelta

# Модель напоминаний с вероятностным сдвигом по дате
# TODO: подумать надо обеспечением 100% вероятности срабатывания уведомления
repeat_model_with_shift = (
    lambda a: a - datedelta.relativedelta(days=1),
    lambda a: a - datedelta.relativedelta(days=2),
    lambda a: a - datedelta.relativedelta(days=4),
    lambda a: a - datedelta.relativedelta(weeks=1) + date_shift(acceptable_error=1),
    lambda a: a - datedelta.relativedelta(weeks=2) + date_shift(acceptable_error=1),
    lambda a: a - datedelta.relativedelta(months=1) + date_shift(),
    lambda a: a - datedelta.relativedelta(months=2) + date_shift(),
    lambda a: a - datedelta.relativedelta(months=6) + date_shift(),
    lambda a: a - datedelta.relativedelta(years=1) + date_shift(acceptable_error=0),
    lambda a: a - datedelta.relativedelta(years=2) + date_shift(acceptable_error=0)
)

# Модель напоминаний без сдвига по дате
repeat_model_without_shift = (
    lambda a: a - datedelta.relativedelta(days=1),
    lambda a: a - datedelta.relativedelta(days=2),
    lambda a: a - datedelta.relativedelta(days=4),
    lambda a: a - datedelta.relativedelta(weeks=1),
    lambda a: a - datedelta.relativedelta(weeks=2),
    lambda a: a - datedelta.relativedelta(months=1),
    lambda a: a - datedelta.relativedelta(months=2),
    lambda a: a - datedelta.relativedelta(months=6),
    lambda a: a - datedelta.relativedelta(years=1),
    lambda a: a - datedelta.relativedelta(years=2)
)

# Тестовая модель напоминаний: напоминания каждый день
# в течение месяца после запоминания
test_repeat_model = [lambda a: a - datedelta.relativedelta(days=i) for i in range(32)]

repeat_model = repeat_model_without_shift


def date_shift(acceptable_error=3):
    """Сдвиг даты уведомления на N дней вперед или назад"""

    delta = datedelta.relativedelta(days=randint(0, acceptable_error))
    return delta if choice('+-') == '+' else -delta


def get_all_dates_for_notification():
    now = datetime.datetime.now().date()

    for model in repeat_model:
        yield model(now)


class RemindingModel:
    """Класс с моделью данных напоминания"""

    def __init__(
            self, caption, year, link, author_name,
            author_birthday, author_death_day, memo_date
    ):
        self.caption = caption
        self.year = year
        self.link = link
        self.author_name = author_name
        self.author_birthday = author_birthday
        self.author_death_day = author_death_day
        self.memo_date = memo_date

    def __str__(self):
        str_model = (
            'Стихотворение: {caption} ({year})\n'
            'Ссылка: {link}\n'
            'Автор: {author_name} ({birthday} - {death_day})\n'
            'Дата запоминания: {memo_date}')

        return str_model.format(
            caption=self.caption,
            year=self.year,
            link=self.link,
            author_name=self.author_name,
            birthday=self.author_birthday,
            death_day=self.author_death_day,
            memo_date=self.memo_date
        )
