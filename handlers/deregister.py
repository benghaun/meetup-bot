from telegram import Update
from telegram.ext import CallbackContext

from .handler_decorator import error_handler
from .db.user import get_user_by_chat_id, remove_user_by_chat_id


@error_handler
def deregister_handler(update: Update, context: CallbackContext) -> None:
    current_user = get_user_by_chat_id(update.message.chat_id)
    if current_user is None:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='You are not registered.')
        return

    remove_user_by_chat_id(update.message.chat_id)
    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text='Deregistration successful')
