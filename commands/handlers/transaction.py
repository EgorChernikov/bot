import logging
from datetime import datetime

from commands.handlers.start import start_command_handler
from context.base import Session
from context.entities.asset import Asset
from context.entities.transaction import Transaction

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Определения состояний для разговора на высшем уровне
SELECTING_ACTION = map(chr, range(1))
# Определения состояний для диалога второго уровня
SELECTING_ADD_WITHDRAW, SELECTING_EXCHANGE_FIRST, SELECTING_EXCHANGE_SECOND = map(chr, range(1, 4))
# Определения состояний для описания беседы
SELECTING_FEATURE, FIRST_INPUT, SECOND_INPUT = map(chr, range(4, 7))
# Мета-состояния
STOPPING, SHOWING = map(chr, range(7, 9))
# завершение беседы
END = ConversationHandler.END

# Различные константы для этого примера
(
    FIRST_ASSET,
    SECOND_ASSET,
    START_OVER,
    ACTION,
    FIRST_AMOUNT,
    SECOND_AMOUNT,
) = map(chr, range(9, 15))


# Top level conversation callbacks
def __transaction_handler(update: Update, context: CallbackContext) -> str:
    text = "Please select transaction type:\n"
    buttons = [
        [
            InlineKeyboardButton(text='Add', callback_data='ADD'),
            InlineKeyboardButton(text='Withdraw', callback_data='WITHDRAW'),
            InlineKeyboardButton(text='Exchange', callback_data='EXCHANGE'),
        ],
        [
            InlineKeyboardButton(text='Nevermind...', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return SELECTING_ACTION


def show_data(update: Update, context: CallbackContext) -> str:
    user_data = context.user_data
    execute_a_transaction = True

    text = f" {user_data[ACTION]} {user_data[FIRST_ASSET]} {user_data[FIRST_AMOUNT]}"
    if user_data[ACTION] == 'EXCHANGE':
        text += f" {user_data[SECOND_ASSET]} {user_data[SECOND_AMOUNT]}"
        if not (user_data[SECOND_AMOUNT].isdigit()):
            execute_a_transaction = False

    if not (user_data[FIRST_AMOUNT].isdigit()):
        execute_a_transaction = False

    if execute_a_transaction:
        session = Session()
        user_id = update.effective_user.id
        first_amount = float(user_data[FIRST_AMOUNT])

        if user_data[ACTION] == 'ADD':
            usd_asset = Transaction(user_id, datetime.now(), user_data[FIRST_ASSET], first_amount)
            session.add(usd_asset)
        elif user_data[ACTION] == 'WITHDRAW':
            usd_asset = Transaction(user_id, datetime.now(), user_data[FIRST_ASSET], -first_amount)
            session.add(usd_asset)
        elif user_data[ACTION] == 'EXCHANGE':
            usd_asset = Transaction(user_id, datetime.now(), user_data[FIRST_ASSET], -first_amount)
            session.add(usd_asset)

            second_amount = float(user_data[SECOND_AMOUNT])

            usd_asset = Transaction(user_id, datetime.now(), user_data[SECOND_ASSET], second_amount)
            session.add(usd_asset)
        session.commit()
        text += f"\nThe transaction was successfully completed!"
        session.close()
    else:
        text += "\nInput error! transaction failed"
    buttons = [
        [
            InlineKeyboardButton(text='Back', callback_data=str(END))
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True

    return SHOWING


def end(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)
    return END


def end_describing(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    context.user_data.clear()
    context.user_data[START_OVER] = True
    __transaction_handler(update, context)
    return END


def stop_nested(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('Okay, bye.')
    return STOPPING


def stop(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    text = 'Okay, bye.'
    update.callback_query.edit_message_text(text=text)
    return END


def select_first_asset(update: Update, context: CallbackContext) -> str:
    buttons = []
    session = Session()
    for asset in session.query(Asset).all():
        buttons.append(InlineKeyboardButton(text=asset.name, callback_data=asset.name))
    session.close()
    buttons = buttons, [InlineKeyboardButton(text='Back', callback_data=str(END))]

    keyboard = InlineKeyboardMarkup(buttons)
    if not context.user_data.get(START_OVER):
        context.user_data[ACTION] = update.callback_query.data
        text = 'Please select a asset.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        # Но после того, как мы это сделаем, нам нужно отправить новое сообщение
    else:
        text = 'Got it! Please select a feature to update.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    if context.user_data[ACTION] == 'EXCHANGE':
        return SELECTING_EXCHANGE_FIRST
    else:
        return SELECTING_ADD_WITHDRAW


def select_level_exchange_second(update: Update, context: CallbackContext) -> str:
    buttons = []
    user_data = context.user_data
    session = Session()
    for asset in session.query(Asset).all():
        if user_data[FIRST_ASSET] != asset.name:
            buttons.append(InlineKeyboardButton(text=asset.name, callback_data=asset.name))
    session.close()
    buttons = buttons, [InlineKeyboardButton(text='Back', callback_data=str(END))]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text="Please select a second asset", reply_markup=keyboard)

    return SELECTING_EXCHANGE_SECOND


def ask_for_input(update: Update, context: CallbackContext) -> str:
    context.user_data[FIRST_ASSET] = update.callback_query.data
    text = 'Enter the amount.'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return FIRST_INPUT


def ask_for_second_input(update: Update, context: CallbackContext) -> str:
    context.user_data[SECOND_ASSET] = update.callback_query.data
    text = 'Enter the second amount.'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return SECOND_INPUT


def save_input_first_amount(update: Update, context: CallbackContext) -> str:
    context.user_data[FIRST_AMOUNT] = update.message.text
    return select_level_exchange_second(update, context)


def save_input(update: Update, context: CallbackContext) -> str:
    context.user_data[FIRST_AMOUNT] = update.message.text
    context.user_data[START_OVER] = True
    return show_data(update, context)


def save_input_second_amount(update: Update, context: CallbackContext) -> str:
    context.user_data[SECOND_AMOUNT] = update.message.text
    context.user_data[START_OVER] = True
    return show_data(update, context)


# Настройка обработчика ADD и WITHDRAW
selecting_add_withdraw = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(select_first_asset, pattern='^ADD$|^WITHDRAW$')],
    states={
        SELECTING_ADD_WITHDRAW: [
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CallbackQueryHandler(ask_for_input)
        ],
        FIRST_INPUT: [MessageHandler(Filters.text & ~Filters.command, save_input)],
    },
    fallbacks=[
        CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
        CommandHandler('stop', stop_nested),
    ],
    map_to_parent={
        END: SELECTING_ACTION,
        STOPPING: END,
    },
)

# Настройка обработчика EXCHANGE
selecting_exchange = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
        CallbackQueryHandler(ask_for_input)
    ],
    states={
        FIRST_INPUT: [MessageHandler(Filters.text & ~Filters.command, save_input_first_amount)],
        SELECTING_EXCHANGE_SECOND: [
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CallbackQueryHandler(ask_for_second_input)
        ],
        SECOND_INPUT: [MessageHandler(Filters.text & ~Filters.command, save_input_second_amount)],
    },
    fallbacks=[
        CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
        CommandHandler('stop', stop_nested),
    ],
    map_to_parent={
        END: SELECTING_ACTION,
        STOPPING: END,
    },
)

selection_handlers = [
    selecting_add_withdraw,
    CallbackQueryHandler(select_first_asset, pattern='^EXCHANGE$'),
    CallbackQueryHandler(stop, pattern='^' + str(END) + '$'),
]
transaction_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('transaction', __transaction_handler)],
    states={
        SELECTING_ACTION: selection_handlers,
        SELECTING_ADD_WITHDRAW: [selection_handlers],
        SELECTING_EXCHANGE_FIRST: [selecting_exchange],
        STOPPING: [CommandHandler('transaction', __transaction_handler)],
    },
    fallbacks=[CommandHandler('start', start_command_handler)],
)
