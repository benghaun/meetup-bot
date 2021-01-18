from telegram import Update
from telegram.ext import CallbackContext

from .handler_decorator import error_handler
from .db.event import get_event
from .db.multidate_event import get_multidate_event


@error_handler
def attendance_handler(update: Update, context: CallbackContext):
    event = get_event()
    multidate_event = get_multidate_event()
    if event is None and multidate_event is None:
        context.bot.sendMessage(
            chat_id=update.message.chat_id, text='There is no event happening')
    elif event is not None:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text=event.attendance())
    else:
        context.bot.sendMessage(
            chat_id=update.message.chat_id, text=multidate_event.attendance())
