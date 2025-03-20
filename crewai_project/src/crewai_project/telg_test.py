import requests
import time
import json

# Replace with your bot token
BOT_TOKEN = '8094075847:AAFUuaPGiLveaJwqSEuHTRYGriW_AIUhMDs'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def get_updates(offset=None):
    url = f'{BASE_URL}/getUpdates'
    params = {'offset': offset, 'timeout': 30} if offset else {'timeout': 30}
    response = requests.get(url, params=params)
    return response.json().get('result', [])

def send_message(chat_id, text):
    url = f'{BASE_URL}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=data)
    return response.json()



def handle_updates(updates):
    for update in updates:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            if 'text' in message:
                text = message['text']
                # Handle text message
                send_message(chat_id, f"your message well recieved: {text}")
           

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates:
            handle_updates(updates)
            offset = updates[-1]['update_id'] + 1
        time.sleep(1)

if __name__ == '__main__':
    main()