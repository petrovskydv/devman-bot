import logging
import time
import os

import requests
from pprint import pprint
from dotenv import load_dotenv
import telegram

load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
devman_token = os.getenv('DEVMAN_TOKEN')
bot = telegram.Bot(token=telegram_token)

# add filemode="w" to overwrite
logging.basicConfig(level=logging.DEBUG)


# headers = {
#     'Authorization': f'Token {telegram_token}'
# }
#
# params = {
#     'timestamp': ''
# }

# def send_telergam_message(text):
#     bot = telegram.Bot(token=telegram_token)
#     bot.send_message(chat_id=telegram_chat_id,
#                      text=text,
#                      parse_mode=telegram.ParseMode.HTML)


def get_checks(token):
    headers = {
        'Authorization': f'Token {token}'
    }
    response = requests.get('https://dvmn.org/api/user_reviews/', headers=headers)
    response.raise_for_status()
    answ = response.json()
    pprint(answ)


def long_pooling_check(token):
    headers = {
        'Authorization': f'Token {token}'
    }

    params = {
        'timestamp': ''
    }
    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
            answ = response.json()
            pprint(answ)
            if answ['status'] == 'timeout':
                print(answ['timestamp_to_request'])
                params['timestamp'] = answ['timestamp_to_request']
                pprint(params)
            elif answ['status'] == 'found':
                lesson_title = answ['new_attempts'][0]['lesson_title']
                lesson_url = answ['new_attempts'][0]['lesson_url']
                if answ['new_attempts'][0]['is_negative']:
                    next_step = 'Необходимо доработать решение.'
                else:
                    next_step = 'Решение принято. Можно приступать к следующему уроку!'
                message = f'Проверена работа "{lesson_title}"\nhttps://dvmn.org{lesson_url}\n{next_step}'
                print(message)
                # send_telergam_message(message)
                bot.send_message(chat_id=telegram_chat_id,
                                 text=message)
                print(answ['last_attempt_timestamp'])
                params['timestamp'] = answ['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            print("\n Переподключение к серверу \n")
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            print("\n Потеря связи \n")
            time.sleep(5)


if __name__ == '__main__':
    # main()
    # response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
    # response.raise_for_status()
    # answ = response.json()
    # pprint(answ)

    # get_checks(devman_token)

    long_pooling_check(devman_token)
    # send_telergam_message()
