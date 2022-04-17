import io

from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, CommandHandler

from context.base import Session
from context.entities.asset import Asset
from context.entities.transaction import Transaction
from sqlalchemy import func
import matplotlib.pyplot as plt

BALANCE_SHEET_REPORT = map(chr, range(1))
END = ConversationHandler.END


def stop(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Okay, bye.')
    return END


def balance_sheet_report(update: Update, context: CallbackContext) -> str:
    session = Session()
    user_id = update.effective_user.id
    message = 'Your balance\n'
    sizes = []
    labels = []
    for asset in session.query(Asset).all():
        balance = session.query(func.sum(Transaction.amount)) \
            .filter(Transaction.asset_name == asset.name) \
            .filter(Transaction.user_id == user_id).first()[0]

        balance = balance if balance is not None else 0
        message += f'{asset.name}: {balance} ({balance * asset.price_usd}$)\n'

        if balance > 0:
            sizes.append(balance * asset.price_usd)
            labels.append(asset.name)
    session.close()

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')

    with io.BytesIO() as buf:
        plt.savefig(buf, format='png')
        buf.seek(0)
        context.bot.send_photo(update.effective_chat.id, buf)

    update.message.reply_text(text=message)

    return END


balance_command_handler = ConversationHandler(
    entry_points=[CommandHandler('balance', balance_sheet_report)],
    states={
        END: [CallbackQueryHandler(stop, pattern='^' + str(END) + '$')]
    },
    fallbacks=[CallbackQueryHandler(stop, pattern='^' + str(END) + '$')]
)
