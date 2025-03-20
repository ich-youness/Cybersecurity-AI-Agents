#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crewai_project.crew import CrewaiProject
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

os.environ['GEMINI_API_KEY'] = "AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k"
TELEGRAM_BOT_TOKEN = "8094075847:AAFUuaPGiLveaJwqSEuHTRYGriW_AIUhMDs"
bot_username = "@V01_PentReconDBBot"


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Send me a domain or IP to scan.")

async def responses(update: Update, context: ContextTypes):
   message_type = update.message.chat.type
   message = update.message.text
   return message

def run():
    """
    Run the crew.
    """
    target = responses()
    # target = str(input("give me the name of the website and a description of the scan: "))
    #options = str(input("Enter the options to use on nmap: "))
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        "target": target,
        # "options": options,

    }
    
    try:
        CrewaiProject().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CrewaiProject().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CrewaiProject().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CrewaiProject().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
