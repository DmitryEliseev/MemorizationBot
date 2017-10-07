import datetime
import dateutil.relativedelta as datedelta

repeat_model = (
    lambda a: a - datedelta.relativedelta(days=1),
    lambda a: a - datedelta.relativedelta(days=2),
    lambda a: a - datedelta.relativedelta(days=4),
    lambda a: a - datedelta.relativedelta(weeks=1),
    lambda a: a - datedelta.relativedelta(weeks=2),
    lambda a: a - datedelta.relativedelta(months=1),
    lambda a: a - datedelta.relativedelta(months=2),
    lambda a: a - datedelta.relativedelta(months=3),
    lambda a: a - datedelta.relativedelta(years=1),
    lambda a: a - datedelta.relativedelta(years=2)
)


def get_all_dates_for_notification():
    now = datetime.datetime.now().date()

    for model in repeat_model:
        yield model(now)


class RemindingModel:
    def __init__(self, caption, link):
        self.caption = caption
        self.link = link
