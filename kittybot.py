import json
import logging
import os
import sys
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import exceptions

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TOKEN')

handler_CP1251 = logging.FileHandler(filename='cp1251.log')
handler_UTF8 = logging.FileHandler(filename='program.log', encoding='utf-8')
logging.basicConfig(
    level=logging.DEBUG,
    handlers=(handler_UTF8, handler_CP1251),
    format=('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - '
            '%(lineno)s - %(message)s'))

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.CRITICAL)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - '
                              '%(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(formatter)

bot = Bot(token=TELEGRAM_TOKEN)

URL = 'https://api.thecatapi.com/v1/images/search'
NEW_URL = 'https://api.thedogapi.com/v1/images/search'

ANSWERS = {
    'привет': 'Привет, я KittyBot!',
    'Привет': 'Привет, я KittyBot!',
    'hello': 'Hello, I am KittyBot!',
    'Hello': 'Hello, I am KittyBot!',
    'Как дела?': 'Всё замечательно! Надеюсь, и ты в полном порядке!',
    'как дела?': 'Всё замечательно! Надеюсь, и ты в полном порядке!',
    "What's up?": 'I am great! Hopefully, you are great too!',
    "what's up?": 'I am great! Hopefully, you are great too!',
    'что ты умеешь?': ('Я могу поднять тебе настроение! Я могу показать '
                       'тебе кучу картинок с милыми животными.'),
    'Что ты умеешь?': ('Я могу поднять тебе настроение! Я могу показать '
                       'тебе кучу картинок с милыми животными.'),
    'what can you do?': ('I can show you pictures of cuties which probably '
                         'will make you merrier!'),
    'What can you do?': ('I can show you pictures of cuties which probably '
                         'will make you merrier!'),
}


def say_hi(update, context):
    """
    Bot answers to any text messages.
    """
    message_from_user = update.effective_message.text
    chat = update.effective_chat
    keys = ANSWERS.keys()
    if message_from_user in keys:
        answer = ANSWERS[message_from_user]
        context.bot.send_message(chat_id=chat.id, text=answer)
        logger.info('Message was successfully sent.')
    elif message_from_user not in keys:
        answer = ('My name is KittyBot and I can show you pictures of cuties! '
                  'Would you like to see some? If you do, press the '
                  'button below.')
        context.bot.send_message(chat_id=chat.id, text=answer)
        logger.info('Message was successfully sent.')
    else:
        logger.error('Sending message is failed.')
        raise exceptions.MessageError('Sending message is failed.')
    return answer


def get_new_image():
    """
    Gets a new random picture from API server and sends it to the user.
    """
    try:
        response_from_api = requests.get(URL)
    except exceptions.APIResponseError as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response_from_api = requests.get(NEW_URL)
    if response_from_api.status_code != HTTPStatus.OK:
        error_status = response_from_api.status_code
        logger.error(
            f'Error during the request to API server: {error_status}'
        )
        raise exceptions.APIResponseError(
            f'Error during the request to API server: {error_status}'
        )
    try:
        response = response_from_api.json()
    except json.JSONDecodeError as error:
        logger.error(
            f'Response has not inverted into json(): {error}.'
        )
        raise json.JSONDecodeError(
            f'Response has not inverted into json(): {error}.'
        )
    try:
        random_cat = response[0]['url']
    except KeyError:
        logger.error('URL of a picture was not received.')
        raise KeyError('URL of a picture was not received.')
    return random_cat


def new_cat(update, context):
    """
    Sends the new picture which is got from get_new_image() after the user
    press the button /newcat.
    """
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def wake_up(update, context):
    """
    Bot greets the user after he sends the command '/start':
    «Thank you for switching me on».
    """
    chat = update.effective_chat
    name = update.message.chat.first_name
    greeting = 'Thank you for switching me on, {}!'.format(name)
    button = ReplyKeyboardMarkup([['/newcat']], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id,
                             text=greeting,
                             reply_markup=button)
    context.bot.send_photo(chat.id, get_new_image())


def check_token():
    """
    Check the token required for running the entire code in the .env.
    If the token is available function returns True, otherwise - False.
    """
    if TELEGRAM_TOKEN:
        return True
    else:
        return False


def main():
    """
    The main logic of the bot.
    """
    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
