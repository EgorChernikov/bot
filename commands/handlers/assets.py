from telegram import Update
from telegram.ext import CallbackContext

from context.base import Session
from context.entities.asset import Asset


def assets_command_handler(update: Update, context: CallbackContext) -> None:
    session = Session()
    message = 'Available assets:\n'
    for asset in session.query(Asset).all():
        message += f'{asset.name}: {asset.price_usd} USD\n'

    update.message.reply_text(message)

    session.close()
