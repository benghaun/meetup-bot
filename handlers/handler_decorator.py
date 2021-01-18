import traceback
from typing import Callable
from telegram import Update
from telegram.ext import CallbackContext

# not a handler - this is a decorator that wraps every other handler to handle any errors gracefully with logging and user feedback


def error_handler(handler_func: Callable) -> Callable:
    def inner(update: Update, context: CallbackContext):
        try:
            name = update.message.from_user.first_name if update.message is not None else update.callback_query.from_user.first_name
            print('running {} now for user {}'.format(
                handler_func.__name__, name))
            handler_func(update, context)
        except Exception as e:
            print("Error occurred when running handler function {}, error message: {}".format(
                handler_func.__name__, str(e)))
            traceback.print_exc()
            chat_id = update.message.chat_id if update.message is not None else update.callback_query.message.chat_id
            context.bot.sendMessage(chat_id=chat_id,
                                    text='Sorry, an error occurred. Please try again later.')
    return inner
