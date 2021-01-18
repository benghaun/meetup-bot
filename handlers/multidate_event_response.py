import os

from telegram import Update
from telegram.ext import CallbackContext

from .db.multidate_event import get_multidate_event
from .handler_decorator import error_handler
from .keyboards import generate_reply_markup

env = os.environ.get('ENVIRONMENT', 'local')
if (env == 'local'):
    from meetupbot_data import group_chat_id
else:
    # hardcoded for now, but potential future use case for this to be stored in DB per chat
    group_chat_id = os.environ["GROUPCHAT_ID"]


@error_handler
def mutlidate_event_response_handler(update: Update, context: CallbackContext):
    multidate_event = get_multidate_event()
    query = update.callback_query
    if multidate_event is None:
        context.bot.sendMessage(
            chat_id=query.message.chat_id, text='There is no event going on now')
    name = query.from_user.first_name
    selected_date = query.data.split(':')[1]

    if (selected_date != 'OK'):
        multidate_event.dates[selected_date].append(name)
        multidate_event.save()

        # remove selected date from keyboard
        new_keyboard_data = {date: 'date:{}'.format(
            date) for date, going in multidate_event.dates.items() if name not in going}
        new_keyboard_data['OK'] = 'date:OK'
        new_reply_markup = generate_reply_markup(3, new_keyboard_data)
        context.bot.editMessageReplyMarkup(
            chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=new_reply_markup)
    else:
        context.bot.sendMessage(chat_id=group_chat_id,
                                text=multidate_event.attendance())
        context.bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                           message_id=query.message.message_id,
                                           reply_markup=None)
