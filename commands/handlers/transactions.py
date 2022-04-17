from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, \
    Filters

from context.base import Session
from context.entities.transaction import Transaction

TRANSACTION_REPORT, INPUT, NUMBER_OF_ENTRIES = map(chr, range(3))
END = ConversationHandler.END


def stop(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    text = 'Okay, bye.'
    context.user_data.clear()
    update.callback_query.edit_message_text(text=text)

    return END


def transaction_report(update: Update, context: CallbackContext) -> str:
    if (context.user_data[NUMBER_OF_ENTRIES].isdigit()):
        session = Session()
        number_of_entries = int(context.user_data[NUMBER_OF_ENTRIES])
        message = 'Transactions:\n'
        for transaction in session.query(Transaction).order_by(Transaction.datetime.desc()).limit(
                number_of_entries).all():
            message += f'{transaction.datetime.replace(microsecond=0)}   {transaction.asset_name} {transaction.amount}\n'
        session.close()
    else:
        message = 'Input error!'

    buttons = [
        [
            InlineKeyboardButton(text='Back', callback_data=str(END))
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=message, reply_markup=keyboard)

    return TRANSACTION_REPORT


def ask_for_input(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(text='Enter the number of entries.')

    return INPUT


def save_input(update: Update, context: CallbackContext) -> str:
    context.user_data[NUMBER_OF_ENTRIES] = update.message.text

    return transaction_report(update, context)


transactions_handler = ConversationHandler(
    entry_points=[CommandHandler('transactions', ask_for_input)],
    states={
        INPUT: [MessageHandler(Filters.text & ~Filters.command, save_input)],
        TRANSACTION_REPORT: [CallbackQueryHandler(stop, pattern='^' + str(END) + '$')]
    },
    fallbacks=[CallbackQueryHandler(stop, pattern='^' + str(END) + '$')],
)