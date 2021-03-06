import logging
import os
import time
from logging import Handler, LogRecord

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class TelegramBotHandler(Handler):
    def __init__(self, token: str, chat_id: str):
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record: LogRecord):
        logger_bot = telegram.Bot(token=self.token)
        logger_bot.send_message(
            self.chat_id,
            self.format(record)
        )


# noinspection PyBroadException
def long_pooling_check(devman_token, telegram_bot, telegram_chat_id):
    headers = {
        'Authorization': f'Token {devman_token}'
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
                logger.debug('Получен пустой ответ')
                params['timestamp'] = review_result['timestamp_to_request']
            elif review_result['status'] == 'found':
                logger.debug('Получен ответ на задачу')
                solution_attempt = review_result['new_attempts'][0]
                lesson_title = solution_attempt['lesson_title']
                lesson_url = solution_attempt['lesson_url']
                if solution_attempt['is_negative']:
                    next_step = 'Необходимо доработать решение.'
                else:
                    next_step = 'Решение принято. Можно приступать к следующему уроку!'
                message = f'Проверена работа "{lesson_title}"\nhttps://dvmn.org{lesson_url}\n{next_step}'
                telegram_bot.send_message(chat_id=telegram_chat_id, text=message)
                params['timestamp'] = review_result['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            logger.info('Переподключение к серверу')
        except requests.exceptions.ConnectionError:
            logger.info('Потеря связи')
            time.sleep(5)
        except requests.exceptions.HTTPError:
            logger.info('ошибка HTTP')
        except Exception:
            logger.exception('Error')


def main():
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(logging.DEBUG)

    load_dotenv()
    telegram_token = os.environ['TELEGRAM_TOKEN']
    telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
    devman_token = os.environ['DEVMAN_TOKEN']

    logger_handler = TelegramBotHandler(telegram_token, telegram_chat_id)
    logger_handler.setLevel(logging.ERROR)
    logger_handler.formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    logger.addHandler(logger_handler)

    logger.info('Бот запущен')
    telegram_bot = telegram.Bot(token=telegram_token)
    long_pooling_check(devman_token, telegram_bot, telegram_chat_id)


if __name__ == '__main__':
    main()
