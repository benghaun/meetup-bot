from telegram import Update
from telegram.ext import CallbackContext

from .handler_decorator import error_handler


@error_handler
def start_handler(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text=("Hello %s! Want to know about VAYS gatherings, but the chat is too noisy? "
                                  "No fear! I will invite you whenever there is a gathering, "
                                  "and I will let everyone in the group chat know if you're going for the gathering. "
                                  "Type /register to register yourself into this wonderful system!\n\n"
                                  "P.S if you don't know what VAYS is, this bot is probably not for you - it was built for private usage"
                                  % update.message.from_user.first_name))
