import os
from datetime import timedelta

from telegram.ext import Updater, CommandHandler, JobQueue, CallbackQueryHandler
from commands.handlers.assets import assets_command_handler
from commands.handlers.balance import balance_command_handler
from commands.handlers.start import start_command_handler
from commands.handlers.transaction import transaction_conversation_handler
from commands.handlers.transactions import transactions_handler

from commands.jobs.context_actualization.assets_price_actualization import actualize_assets_price


def start_updater() -> None:
    """Starts the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))

    # Get the dispatcher to register handlers.
    dispatcher = updater.dispatcher

    # On different commands - answer in Telegram.
    dispatcher.add_handler(CommandHandler('start', start_command_handler))
    dispatcher.add_handler(CommandHandler('assets', assets_command_handler))
    dispatcher.add_handler(transaction_conversation_handler)
    dispatcher.add_handler(transactions_handler)
    dispatcher.add_handler(balance_command_handler)

    job_queue: JobQueue = updater.job_queue
    job_queue.run_repeating(callback=actualize_assets_price, interval=timedelta(hours=3), first=1)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
