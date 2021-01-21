import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


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
            review_result = response.json()
            if review_result['status'] == 'timeout':
                logger.info('Получен пустой ответ')
                params['timestamp'] = review_result['timestamp_to_request']
            elif review_result['status'] == 'found':
                logger.info('Получен ответ на задачу')
                solution_attempt = review_result['new_attempts'][0]
                lesson_title = solution_attempt['lesson_title']
                lesson_url = solution_attempt['lesson_url']
                if solution_attempt['is_negative']:
                    next_step = 'Необходимо доработать решение.'
                else:
                    next_step = 'Решение принято. Можно приступать к следующему уроку!'
                message = f'Проверена работа "{lesson_title}"\nhttps://dvmn.org{lesson_url}\n{next_step}'
                BOT.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                params['timestamp'] = review_result['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            logger.info("Переподключение к серверу")
        except requests.exceptions.ConnectionError:
            logger.info("Потеря связи")
            time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(logging.INFO)
    logger.info('Бот запущен')

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    DEVMAN_TOKEN = os.getenv('DEVMAN_TOKEN')
    BOT = telegram.Bot(token=TELEGRAM_TOKEN)

    long_pooling_check(DEVMAN_TOKEN)
