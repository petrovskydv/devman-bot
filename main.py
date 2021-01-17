import logging
import time
import os

import requests
from pprint import pprint

telegram_token = os.getenv('TELEGRAN_TOKEN')

# add filemode="w" to overwrite
logging.basicConfig(level=logging.DEBUG)

headers = {
    "Authorization": "Token 11df0520152a6a16bd950b966914f647c2e3ab96"
}

params = {
    'timestamp': ''
}

def main():

    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
            answ = response.json()
            # print(json.dumps(answ, indent=4, ensure_ascii=False))
            print(answ['status'])
            if answ['status'] == 'timeout':
                print(answ['timestamp_to_request'])
                params['timestamp'] = answ['timestamp_to_request']
            elif answ['status'] == 'found':
                print(answ['last_attempt_timestamp'])
                params['timestamp'] = answ['last_attempt_timestamp']
        except requests.exceptions.ReadTimeout:
            print("\n Переподключение к серверу \n")
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            print("\n Потеря связи \n")
            time.sleep(5)
            # response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)

        
if __name__ == '__main__':
    # main()
    response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
    response.raise_for_status()
    answ = response.json()
    # print(json.dumps(answ, indent=4, ensure_ascii=False))
    pprint(answ)