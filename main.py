import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DEVMAN_TOKEN = os.getenv('DEVMAN_TOKEN')
BOT = telegram.Bot(token=TELEGRAM_TOKEN)


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
            response_result = response.json()
            if response_result['status'] == 'timeout':
                params['timestamp'] = response_result['timestamp_to_request']
            elif response_result['status'] == 'found':
                lesson_title = response_result['new_attempts'][0]['lesson_title']
                lesson_url = response_result['new_attempts'][0]['lesson_url']
                if response_result['new_attempts'][0]['is_negative']:
                    next_step = 'Необходимо доработать решение.'
                else:
                    next_step = 'Решение принято. Можно приступать к следующему уроку!'
                message = f'Проверена работа "{lesson_title}"\nhttps://dvmn.org{lesson_url}\n{next_step}'
                BOT.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                params['timestamp'] = response_result['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            print("\n Переподключение к серверу \n")
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            print("\n Потеря связи \n")
            time.sleep(5)


if __name__ == '__main__':
    long_pooling_check(DEVMAN_TOKEN)
