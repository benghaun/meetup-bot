from telegram import Update
from telegram.ext import CallbackContext

from .db.user import get_user_by_chat_id, add_user
from .handler_decorator import error_handler


@error_handler
def register_handler(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'private':
        existing_user = get_user_by_chat_id(update.message.chat_id)
        if existing_user is not None:
            context.bot.sendMessage(chat_id=update.message.chat_id,
                                    text='Hi, you are already registered!')
            return
        add_user(update.message.from_user.first_name,
                 update.message.chat_id, update.message.from_user.username)
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='Registration successful!')
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='Hi, please register in a private chat with me instead!')
