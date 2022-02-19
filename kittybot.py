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


def say_hi(update, context):
    """
    Bot answers to any text messages.
    """
    answer = 'Привет, я KittyBot!'
    chat = update.effective_chat
    try:
        context.bot.send_message(chat_id=chat.id, text=answer)
        logger.info('Message succesfully sent.')
    except exceptions.MessageError as error:
        logger.error(f'Message was not send to the user: {error}')
        raise exceptions.MessageError(
            f'Message was not send to the user: {error}'
        )


def get_new_image():
    """
    Gets a new random picture from API server and sends it to the user.
    """
    try:
        response_from_api = requests.get(URL)
    except exceptions.APIResponseError as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response = requests.get(NEW_URL)
    if response_from_api.status_code != HTTPStatus.OK:
        error_status = response_from_api.status_code
        logger.error(
            f'Error during the request to API server: {error_status}'
        )
        raise exceptions.APIResponseError(
            f'Error during the request to API server: {error_status}'
        )
    response = response_from_api.json()
    random_cat = response[0].get('url')
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
    token_approved = check_token()
    if not token_approved:
        logger.critical('Mandatory token from .env is not available.')
        raise ValueError('Mandatory token from .env is not available.')
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
