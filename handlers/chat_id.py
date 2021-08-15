from telegram import Update
from telegram.ext import CallbackContext

from .handler_decorator import error_handler


@error_handler
def chat_id_handler(update: Update, context: CallbackContext) -> None:
    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text=(update.message.chat_id))
