import telebot
from config import SETTINGS
import constants

from database import get_all_users_id
from database import get_all_notifications
from database import insert_notification

bot = telebot.TeleBot(SETTINGS.TOKEN)


@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id,
        constants.MSG_START_COMMAND
    )


@bot.message_handler(content_types=['text'])
def add_notification(message):
    message_text = message.text
    if message_text.startswith('/add'):
        process_adding_new_item(message)

    bot.send_message(
        message.chat.id,
        constants.MSG_ADD_COMMAND
    )


def send_notifications():
    for user_id in get_all_users_id():
        for notification in get_all_notifications(user_id):
            bot.send_message(
                user_id,
                '{}{}'.format(
                    notification.caption,
                    '\n' + notification.link if notification.link else ''
                )
            )


def process_adding_new_item(message):
    message_text = message.text.replace("/add ", "")
    message_text = message_text.split('#')

    if len(message_text) == 1:
        insert_notification(message.chat.id, message_text[0])
        bot.send_message(
            message.chat.id,
            constants.MSG_SUCCESS_ADDING_NOTIFICATION.format(" ")
        )

    elif len(message_text) == 2:
        insert_notification(
            message.chat.id,
            message_text[0],
            message_text[1]
        )

        bot.send_message(
            message.chat.id,
            constants.MSG_SUCCESS_ADDING_NOTIFICATION.format(
                " cо ссылкой"
            )
        )

    else:
        bot.send_message(
            message.chat.id,
            constants.ERROR_WRONG_ADD_FORMAT
        )


if __name__ == '__main__':
    bot.send_message(65305591, "Бот запущен")
    bot.polling(none_stop=True)
