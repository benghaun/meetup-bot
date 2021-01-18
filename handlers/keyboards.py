from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

going_button = InlineKeyboardButton(text="I'm going!",
                                    callback_data='single_event:going')
notgoing_button = InlineKeyboardButton(text="I can't make it",
                                       callback_data='single_event:not_going')
maybe_button = InlineKeyboardButton(text="Maybe, I'm not sure yet.",
                                    callback_data='single_event:maybe')
cancel_button = InlineKeyboardButton(text="Cancel",
                                     callback_data='single_event:cancel')
event_invite_custom_keyboard = [
    [going_button, notgoing_button], [maybe_button]]
event_invite_reply_markup = InlineKeyboardMarkup(event_invite_custom_keyboard)

event_invite_custom_keyboard_without_maybe = [[going_button, notgoing_button]]
event_invite_reply_markup_without_maybe = InlineKeyboardMarkup(
    event_invite_custom_keyboard_without_maybe)

event_invite_custom_keyboard_with_cancel = event_invite_custom_keyboard = [
    [going_button, notgoing_button], [maybe_button, cancel_button]]
event_invite_reply_markup_with_cancel = InlineKeyboardMarkup(
    event_invite_custom_keyboard_with_cancel)


def generate_reply_markup(cols: int, data: Dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = []
    subkeyboard = []
    for label, callback_data in data.items():
        if len(subkeyboard) < 3:
            subkeyboard.append(InlineKeyboardButton(
                text=label, callback_data=callback_data))
        else:
            keyboard.append(subkeyboard)
            subkeyboard = [InlineKeyboardButton(
                text=label, callback_data=callback_data)]

    if subkeyboard != []:
        keyboard.append(subkeyboard)
    return InlineKeyboardMarkup(keyboard)
