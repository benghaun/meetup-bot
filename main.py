import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os

from handlers import (start_handler,
                      register_handler,
                      deregister_handler,
                      create_event_handler,
                      single_event_response_handler,
                      change_handler,
                      attendance_handler,
                      del_event_handler,
                      create_multidate_event_handler,
                      mutlidate_event_response_handler)

env = os.environ.get('ENVIRONMENT', 'local')
if (env == 'local'):
    from meetupbot_data import token, group_chat_id
    TOKEN = token
else:
    TOKEN = os.environ["TOKEN"]
    # hardcoded for now, but potential future use case for this to be stored in DB per chat
    group_chat_id = os.environ["GROUPCHAT_ID"]

PORT = int(os.environ.get('PORT', '5000'))

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


# handler initialization
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('register', register_handler))
dispatcher.add_handler(CommandHandler('deregister', deregister_handler))
dispatcher.add_handler(CommandHandler('create_event', create_event_handler))
dispatcher.add_handler(CommandHandler('change', change_handler))
dispatcher.add_handler(CommandHandler('attendance', attendance_handler))
dispatcher.add_handler(CommandHandler('del_event', del_event_handler))
dispatcher.add_handler(CommandHandler(
    'create_multidate_event', create_multidate_event_handler))

dispatcher.add_handler(CallbackQueryHandler(
    single_event_response_handler, pattern="^single_event:"))
dispatcher.add_handler(CallbackQueryHandler(
    mutlidate_event_response_handler, pattern="^date:"))

if env == 'local':
    updater.start_polling()
    print('Started long polling for local development')
    updater.idle()

elif env == 'production':
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.setWebhook(os.environ["HEROKU_LINK"] + TOKEN)
else:
    raise Exception('Invalid environment')
