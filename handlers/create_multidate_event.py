from telegram import Update
from telegram.ext import CallbackContext
from .handler_decorator import error_handler
from .db.multidate_event import create_multidate_event
from .db.user import get_users
from .keyboards import generate_reply_markup


@error_handler
def create_multidate_event_handler(update: Update, context: CallbackContext) -> None:
    dates_str = context.args[-1]
    if dates_str[0] != '{' or dates_str[-1] != '}':
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='Your command has an incorrect format. Type the event info first, then the dates within curly braces({date1,date2,...})')
        return
    users = get_users()
    dates = dates_str[1:-1].split(',')
    event_info = ' '.join(context.args[:-1])
    create_multidate_event(dates, event_info)
    keyboard_data = {date: 'date:{}'.format(date) for date in dates}
    keyboard_data['OK'] = 'date:OK'
    keyboard_markup = generate_reply_markup(
        3, keyboard_data)
    for user in users:
        context.bot.sendMessage(
            chat_id=user.chat_id, text='You have been invited to the following event: {}'.format(event_info), reply_markup=keyboard_markup)
