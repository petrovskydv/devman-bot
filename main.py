import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__file__)


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
            decoded_response_body = response.json()
            if decoded_response_body['status'] == 'timeout':
                logger.info('Получен пустой ответ')
                params['timestamp'] = decoded_response_body['timestamp_to_request']
            elif decoded_response_body['status'] == 'found':
                logger.info('Получен ответ на задачу')
                solution_attempt = decoded_response_body['new_attempts'][0]
                lesson_title = solution_attempt['lesson_title']
                lesson_url = solution_attempt['lesson_url']
                if solution_attempt['is_negative']:
                    next_step = 'Необходимо доработать решение.'
                else:
                    next_step = 'Решение принято. Можно приступать к следующему уроку!'
                message = f'Проверена работа "{lesson_title}"\nhttps://dvmn.org{lesson_url}\n{next_step}'
                BOT.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                params['timestamp'] = decoded_response_body['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            logger.info("Переподключение к серверу")
        except requests.exceptions.ConnectionError:
            logger.info("Потеря связи")
            time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info('проверка сообщений')

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    DEVMAN_TOKEN = os.getenv('DEVMAN_TOKEN')
    BOT = telegram.Bot(token=TELEGRAM_TOKEN)

    long_pooling_check(DEVMAN_TOKEN)
