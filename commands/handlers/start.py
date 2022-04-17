from telegram import Update
from telegram.ext import CallbackContext


def start_command_handler(update: Update, context: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    update.message.reply_text(
        'Hey! This bot will help you track and balance your investment portfolio!\n'
        '/start\n'
        '/assets\n'
        '/transaction\n'
        '/transactions\n'
        '/balance\n'
    )
