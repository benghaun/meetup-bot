from telegram import Update
from telegram.ext import CallbackContext

from .keyboards import event_invite_reply_markup
from .db.event import create_event, get_event
from .db.multidate_event import get_multidate_event
from .db.user import get_users, User
from .handler_decorator import error_handler


@error_handler
def create_event_handler(update: Update, context: CallbackContext) -> None:
    info = ' '.join(context.args)
    if update.message.chat.type == 'private':
        existing_event = get_event()
        existing_multidate_event = get_multidate_event()
        if existing_event is not None or existing_multidate_event is not None:
            context.bot.sendMessage(chat_id=update.message.chat_id,
                                    text='An event already exists, please use /del_event to delete it first')
            return
        users = get_users()
        create_event(info, update.message.chat_id,
                     update.message.from_user.first_name, users)
        for user in users:
            if user.chat_id != update.message.chat_id:
                context.bot.sendMessage(
                    chat_id=user.chat_id, text='You have been invited to the following event: {}'.format(info), reply_markup=event_invite_reply_markup)
        context.bot.sendMessage(
            chat_id=update.message.chat_id, text='Event created successfully')
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                                text='Please create the event in a private message with me instead')
