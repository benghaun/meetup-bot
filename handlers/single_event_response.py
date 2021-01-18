import os

from telegram import Update
from telegram.ext import CallbackContext

from .db.event import get_event
from .keyboards import event_invite_reply_markup_without_maybe
from .handler_decorator import error_handler

env = os.environ.get('ENVIRONMENT', 'local')
if (env == 'local'):
    from meetupbot_data import group_chat_id
else:
    # hardcoded for now, but potential future use case for this to be stored in DB per chat
    group_chat_id = os.environ["GROUPCHAT_ID"]


@error_handler
def single_event_response_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    name = query.from_user.first_name
    event = get_event()

    # No event, delete all buttons and inform user
    if event is None:
        context.bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                           message_id=query.message.message_id,
                                           reply_markup=None)
        context.bot.sendMessage(chat_id=query.message.chat_id,
                                text="Hmm, it seems that there isn't an event happening now.")
        return

    # First, remove the user's name from any previous attendance status, in case this function was called from /change
    if name in event.going:
        event.going.remove(name)
    elif name in event.maybe:
        event.maybe.remove(name)
    elif name in event.unresponded:
        event.unresponded.remove(name)
    elif name in event.not_going:
        event.not_going.remove(name)

    # remove buttons from display after they are pressed
    context.bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                       message_id=query.message.message_id,
                                       reply_markup=None)

    # Handle each individual button
    if query.data == 'single_event:going':
        event.going.append(name)

    elif query.data == 'single_event:not_going':
        event.not_going.append(name)

    elif query.data == 'single_event:maybe':
        event.maybe.append(name)
        # remove the 'maybe' button, but keep the other two
        context.bot.editMessageReplyMarkup(chat_id=query.message.chat_id,
                                           message_id=query.message.message_id,
                                           reply_markup=event_invite_reply_markup_without_maybe)
        context.bot.sendMessage(chat_id=query.message.chat_id,
                                text="Alright, if you can confirm, "
                                "just press either of the 'I'm Going!' or 'I can't make it' buttons, "
                                "or use /change to change your attendance status.")

    elif query.data == 'single_event:cancel':
        context.bot.editMessageText(chat_id=query.message.chat_id,
                                    message_id=query.message.message_id,
                                    text='')

    # send updated list of attendees to the group
    context.bot.sendMessage(chat_id=group_chat_id,
                            text=event.attendance())

    event.save()
