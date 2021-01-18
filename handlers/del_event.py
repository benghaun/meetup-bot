from telegram import Update
from telegram.ext import CallbackContext

from .db.event import delete_event, get_event
from .db.multidate_event import get_multidate_event, delete_multidate_event
from .handler_decorator import error_handler


@error_handler
def del_event_handler(update: Update, context: CallbackContext) -> None:
    event = get_event()
    multidate_event = get_multidate_event()
    if event is None and multidate_event is None:
        context.bot.sendMessage(
            chat_id=update.message.chat_id, text='There is currently no event')
        return
    elif event is not None:
        delete_event()
    else:
        delete_multidate_event()
    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text='Event successfully deleted')
