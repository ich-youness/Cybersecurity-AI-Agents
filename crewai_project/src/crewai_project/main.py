#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import time
import json
import requests
from crewai_project.crew import CrewaiProject

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

TOKEN = "8094075847:AAFUuaPGiLveaJwqSEuHTRYGriW_AIUhMDs"
bot_username = "@V01_PentReconDBBot"

# Telegram functions:
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
    # print("data from message send:  ",data)
    response = requests.post(url, data=data)
    return response.json()

def send_document(chat_id, file_path, caption=None):
    """
    Sends a document (e.g., the OWASP ZAP report) to a Telegram chat.
    """
    url = f'{BASE_URL}/sendDocument'
    with open(file_path, 'rb') as file:
        data = {'chat_id': chat_id, 'caption': caption} if caption else {'chat_id': chat_id}
        # print("data from docum: ", data)
        files = {'document': file}
        response = requests.post(url, data=data, files=files)
    return response.json()

# def handle_updates(updates):
#     for update in updates:
#         if 'message' in update:
#             message = update['message']
#             chat_id = message['chat']['id']

#             # print("chat_id from handle: ", chat_id)
#             if 'text' in message:
#                 target = message['text']
#                 inputs = {"target": target}
#                 results = CrewaiProject().crew().kickoff(inputs=inputs)
#                 result = results.raw
#                 # send_message(chat_id, f"Here are your results: \n{result}")
#                 report_path = "crewai_project\nmap_report.txt"
#                 send_document(chat_id, report_path, caption="Here is your nmap scan report.")
#                 return target

def main_telegram():
    offset = None
    print("Listening ... ")
    
    # Send initial message asking for website and type of scan
    updates = get_updates(offset)
    if updates:
        chat_id = updates[-1]['message']['chat']['id']
        
        send_message(chat_id, "Which website and type of scan do you want?")
        offset = updates[-1]['update_id'] + 1  # Update offset to avoid reprocessing old messages
    
    # Wait for user's response
    while True:
        updates = get_updates(offset)
        if updates:
            last_update = updates[-1]
            if 'message' in last_update:
                message = last_update['message']
                if 'text' in message:
                    target = message['text']
                    inputs = {"target": target}
                    results = CrewaiProject().crew().kickoff(inputs=inputs)
                    
                    # Wait for the scan to complete
                    # while not results.is_complete:
                    #     print("Waiting for the scan to complete...")
                    #     time.sleep(5)
                    
                    result = results.raw
                    # nmap_report =r"D:\Stage_PFE\CrewAI\crewai_project\nmap_report.txt"
                    # with open(nmap_report, "r") as f:
                    #     result = f.read()
                    # # send_message(chat_id, f"Here are your results: \n{result}")
                    # send_document(chat_id, nmap_report, caption="Here is your nmap scan report.")
                    return target
            offset = updates[-1]['update_id'] + 1  # Update offset after processing
        time.sleep(1)
def run():
    """
    Run the crew
    """
    main_telegram()
    # target = input("Enter the website and type of scan you want: ")
    # inputs = {
    #     'topic': 'AI LLMs',
    #     'current_year': str(datetime.now().year),
    #     "target": target,
    # }
    
    # try:
    #     CrewaiProject().crew().kickoff(inputs=inputs)
    #     result = results.raw
    #     send_message(chat_id, f"Here are your results: \n{result}")
    # except Exception as e:
    #     raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()