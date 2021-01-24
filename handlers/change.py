from telegram import Update
from telegram.ext import CallbackContext

from .db.event import get_event
from .db.multidate_event import get_multidate_event
from .handler_decorator import error_handler
from .keyboards import event_invite_reply_markup_with_cancel, generate_reply_markup


@error_handler
def change_handler(update: Update, context: CallbackContext):
    event = get_event()
    multidate_event = get_multidate_event()
    if event is None and multidate_event is None:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='There is currently no event.')
        return

    name = update.message.from_user.first_name
    if update.message.chat.type != 'private':
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text="If you wish to change your attendance status, "
                                "do so in a private chat with me.")
        return

    # single date event
    if event is not None:
        current_status = 'Unresponded'
        if name in event.going:
            current_status = 'Going'
        elif name in event.not_going:
            current_status = 'Not going'
        elif name in event.maybe:
            current_status = 'Maybe'
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text="Would you like to change your attendance status for %s?\n"
                                "Your current status is %s." % (
                                    event.info, current_status),
                                reply_markup=event_invite_reply_markup_with_cancel)
        return

    # multidate event
    keyboard_data = {date if name not in going else date + ' ✅': 'date:{}'.format(date
                                                                                  ) for date, going in multidate_event.dates.items()}
    keyboard_data['OK'] = 'date:OK'
    keyboard_markup = generate_reply_markup(
        3, keyboard_data)

    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text="Okay, select the new dates that you can make it, and press OK when you are done."
                            " Similarly, if you cannot make it on any of the dates, just press OK.",
                            reply_markup=keyboard_markup)
