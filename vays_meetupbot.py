#####################################################################################
#This bot is for organizing meetups                                         
#It sends a message to every registered individual and invites them to the event    
#It then updates the attendance of each inidvidual on the group chat   
#It makes use of Heroku Postgres to store the information on the cloud
#####################################################################################

import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler,Filters
import os
import string
import psycopg2
import urlparse
import ast

#Initiialization for storage in POSTGRESQL database
url = urlparse.urlparse(os.environ["HEROKU_POSTGRESQL_RED_URL"])

#Initialization for webhook
TOKEN = os.environ["TOKEN"]
PORT = int(os.environ.get('PORT', '5000'))

#other generic initializations for the bot
bot = telegram.Bot(token = TOKEN)
bot.setWebhook(webhook_url = os.environ["HEROKU_LINK"] + TOKEN)
updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher
group_chatid = os.environ["GROUPCHAT_ID"]


##
# class that represents an event
# under __init__, row represents raw info that was obtained from the database
# going: String representing people who are going
# not_going: String representing people who are not going
# maybe: String representing people who may be going
# unresponded: String representing people who have not responded
# info: String representing the description of the event
# user_dictionary: Dictionary with names as keys and chat ids as values
##
class Event(object):
    def __init__(self, row):
        self.going = row[0]
        self.not_going = row[1]
        self.maybe = row[2]
        self.unresponded = row[3]
        self.info = row[4]
        self.user_dictionary = ast.literal_eval(row[5])

    # returns a string representing the overall event attendance
    def attendance(self):
        attendance = ("%s\n"
                     "\n"
                     "Going:\n"
                     "%s\n"
                     "Not going:\n"
                     "%s\n"
                     "Maybe:\n"
                     "%s\n"
                     "Unresponded:\n"
                     "%s"%(self.info,self.going,self.not_going,self.maybe,self.unresponded))
        return attendance

    #Deletes all the info for this event
    def clear(self):
        self.going = ''
        self.not_going = ''
        self.maybe = ''
        self.unresponded = ''
        self.info = ''

##
# class that represents a multidate event
# similarly, rows is raw data from the database
# rowS instead of row because there are multiple dates, so multiple rows from the data in the database
# dict: Dictionary with dates (string) as keys, and people going (string) as values
# dates: List of dates for the event
# info: String representing a description of the event
##
class Multidate_event(object):
    def __init__(self,rows):
        self.dict = {}
        self.dates = []
        if rows != []:
            for row in rows:
                self.dict[row[0]] = row[1]
                self.dates.append(row[0])
            self.info = rows[0][2]
        else:
            self.info = ''

    # returns a string representing the attendance for every date
    def attendance(self):
        message = self.info + '\n'
        for i in range(len(self.dates)):
            message += self.dates[i]+':\n'
            message += self.dict[self.dates[i]] + '\n'
        return message


##
# Connects to the database and returns the connection object and its cursor
# The connection object must be closed using conn.close() after all interaction with database is complete
# If the database was changed, conn.commit() must be called before closing to commit the changes
# The cursor is used to perform SQL operations on the database
##
def connect_db():
    conn = psycopg2.connect(
                            database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)
    cur = conn.cursor()
    return conn,cur

##
# Connects to the database and gets the user dictionary
# User dictionary contains names of users as keys, and chat ids as values
# Returns the user dictionary
##
def get_user_dictionary():
    conn,cur = connect_db()  
    cur.execute("SELECT USERDICTIONARY FROM EVENTINFO")
    rows = cur.fetchall()
    row = rows[0]
    user_dictionary = ast.literal_eval(row[0])
    conn.close()
    return user_dictionary

##
# Updates the user dictionary currently in the database
# Used to register/deregister users
##
def update_user_dictionary(new_dict):
    conn,cur = connect_db()
    user_dictionary = str(new_dict).replace("'","''")
    cur.execute("""UPDATE EVENTINFO SET USERDICTIONARY ='%s'"""%(str(user_dictionary)))
    conn.commit()
    conn.close()

##
# Gets the information about the event from the database
# Returns the information as an Event object
# If there is no event, a Event object will still be returned, but with most of its information as empty strings.
##
def get_event():
    conn,cur = connect_db() 
    cur.execute("SELECT GOING,NOTGOING,MAYBE,UNRESPONDED,EVENT,USERDICTIONARY FROM EVENTINFO")
    row = cur.fetchall()[0]
    conn.close()
    return Event(row)

##
# Updates the information about the event in the database
# Mainly used for attendance updating and event deletion
# However, it is also used for event creation
##
def update_event(event):
    conn,cur = connect_db()
    cur.execute("UPDATE EVENTINFO SET GOING = '%s',"
            "NOTGOING = '%s',"
            "MAYBE = '%s',"
            "UNRESPONDED = '%s',"
            "EVENT = '%s'"
            "where ID = 1"%(event.going,event.not_going,event.maybe,event.unresponded,event.info))
    conn.commit()
    conn.close()

##
# Similar to get_event, but for multidate events only
# If there is no event, a multidate_event object will still be returned, but with most of its information as empty strings.
##
def get_multidate_event():
    conn,cur = connect_db()
    cur.execute("SELECT DATE,GOING,EVENT FROM MULTIDATE ORDER BY ID")
    multidate_event = Multidate_event(cur.fetchall())
    conn.commit()
    conn.close()
    return multidate_event

##
# Adds a new multidate event into the database
# Only used when creating new multidate events
# Should not be called if a multidate event already exists
##
def add_multidate_event(event):
    conn,cur = connect_db()
    for i in range(len(event.dates)):
        cur.execute("INSERT INTO MULTIDATE (ID,DATE,GOING,EVENT) VALUES('%d','%s', '', '%s')"%(i,event.dates[i],event.info))

    cur.execute("INSERT INTO MULTIDATE(ID,DATE,GOING,EVENT) VALUES('%d','None','','%s')"%(len(event.dates)+1,event.info))
    cur.execute("INSERT INTO MULTIDATE(ID,DATE,GOING,EVENT) VALUES('%d','Unresponded', '%s', '%s')"%(len(event.dates)+2,event.dict['Unresponded'],event.info))
    conn.commit()
    conn.close()

##
# Updates the current multidate event in the database
# Similarly, used for attendance updating and event deletion
# NOT used for multidate event creation, unlike update_event
##
def update_multidate_event(event):
    conn,cur = connect_db()
    for date in event.dates:
        cur.execute("UPDATE MULTIDATE SET GOING = '%s' WHERE DATE = '%s'"%(event.dict[date],date))
    conn.commit()
    conn.close()

##
# Deletes a multidate event from the database
# Handled differently from single date events due to the different way that multidate events are structured in the database
##
def delete_multidate_event():
    conn,cur = connect_db()
    cur.execute("DELETE FROM MULTIDATE")
    conn.commit()
    conn.close()

##
# Start function, which basically responds to the user when user types /start
##
def start(bot, update):
    bot.sendMessage(chat_id = update.message.chat_id, 
                    text = ("Hello %s! Want to know about VAYS gatherings, but the chat is too noisy? "
                    "No fear! I will invite you whenever there is a gathering, "
                    "and I will let everyone in the group chat know if you're going for the gathering. "
                    "Type /register to register yourself into this wonderful system!"%update.message.from_user.first_name))

dispatcher.add_handler(CommandHandler('start', start))

##
# Register function for users to register themselves into the system
# Called when user types /register
# Adds users into the user dictionary in the database
##
def register(bot,update):
    user_dictionary = get_user_dictionary()
    if update.message.chat.type == 'private':
        if update.message.from_user.first_name not in user_dictionary:
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = 'Registration successful!')
            user_dictionary[update.message.from_user.first_name] = update.message.chat_id
            update_user_dictionary(user_dictionary)
            
        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = 'Hi, you are already registered!')
    else:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'Hi, please register in a private chat with me instead!')

    
dispatcher.add_handler(CommandHandler('register',register))

##
# Opposite of register function, removes users from user dictionary in database
# Called when user types /deregister
##
def deregister(bot,update):
    user_dictionary = get_user_dictionary()
    if update.message.from_user.first_name in user_dictionary:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'Deregistration successful')
        del user_dictionary[update.message.from_user.first_name]
        update_user_dictionary(user_dictionary)

    else:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'You are not registered.')

    
dispatcher.add_handler(CommandHandler('deregister',deregister))

##
#Creation of custom buttons/keyboards for user to respond to invite
#These are declared globally as they are used in multiple functions
##
going_button = telegram.InlineKeyboardButton(text = "I'm going!", 
                                             callback_data = 'single event:going')
notgoing_button = telegram.InlineKeyboardButton(text = "I can't make it", 
                                                callback_data = 'single event:not going')
maybe_button = telegram.InlineKeyboardButton(text = "Maybe, I'm not sure yet.", 
                                             callback_data = 'single event:maybe')
cancel_button = telegram.InlineKeyboardButton(text = "Cancel" , 
                                              callback_data = 'single event:cancel')
custom_keyboard = [[going_button,notgoing_button],[maybe_button]]
reply_markup = telegram.InlineKeyboardMarkup(custom_keyboard)
    

custom_keyboard_with_cancel = [[going_button,notgoing_button],[maybe_button],[cancel_button]]
reply_markup_With_cancel = telegram.InlineKeyboardMarkup(custom_keyboard_with_cancel)



##
# Function for creating an event
# Creates an event as a Event object, and stores it in the database
# Is called when user types /create_event <event info>
# Fails and informs user of failure if there is already an active event, the event was created in a group chat, or if there was no event info provided
##
def create_event(bot,update):
    event = get_event()
    dates = get_multidate_event().dates #to check for multidate event 
    if event.info != '' or dates != []:  
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'There is already an active event, use /del_event to delete it first.')

    elif update.message.chat.type == 'private':
        if update.message.text[14:] != '':
            event.info = update.message.text[14:] 
            #Add creator of event to string of people who are going
            event.going += '%s\n' %update.message.from_user.first_name
            for name in event.user_dictionary:
                if name not in event.going:
                    event.unresponded += '%s\n' %name
            # Send list of attendees to group chat
            bot.sendMessage(chat_id = group_chatid,
                            text = event.attendance())

            #Send invites to all registered users except creator of event
            for user in event.user_dictionary:
                if user == update.message.from_user.first_name:
                    pass
                else:
                    bot.sendMessage(chat_id = event.user_dictionary[user],
                                    text = update.message.text[14:],
                                    reply_markup = reply_markup)

            #Inform event creator of success of event creation
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = 'Event creation successful!')

        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = 'Please include some details of the event.')

    else:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'Please create an event using a private chat with me instead!')

    event.info = event.info.replace("'","''")
    update_event(event)

dispatcher.add_handler(CommandHandler('create_event',create_event))

##
# Function that creates a event with multiple date options
# Creates a multidate event as a Multidate_event object, and stores it in the database
# Similarly to create_event, fails and informs user of failure if there is already an active event, the event was created in a group chat, or if there was no event info provided
# Is called when user types /multidate_event <event info> {date1, date2...}
##
def create_event_multidate(bot,update):
    user_dictionary = get_user_dictionary()
    start_idx = 0
    end_idx = 0
    event = get_event()
    multidate_event = get_multidate_event()
    if event.info != '' or multidate_event.dates != []:  
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'There is already an active event, use /del_event to delete it first.')
        return

    if update.message.chat.type != 'private':
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'Please create an event in a private chat with me instead.')
        return

    #Parsing user input
    for i in range(0,len(update.message.text)):
        if update.message.text[i] == '{':
            if start_idx == 0:
                start_idx = i
            else:
                bot.sendMessage(chat_id = update.message.chat_id,
                                text = 'Your command has an incorrect format. Type the event info first, then the dates within curly braces ({date1, date2, ...})')
                return
        if update.message.text[i] == '}':
            if end_idx == 0:
                end_idx = i
            else:
                bot.sendMessage(chat_id = update.message.chat_id,
                                text = 'Your command has an incorrect format. Type the event info first, then the dates within curly braces ({date1, date2, ...})')
                return
    if (start_idx == 0) or (end_idx == 0):
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'Your command has an incorrect format. Type the event info first, then the dates within curly braces ({date1, date2, ...})')
        return

    multidate_event.info = update.message.text[17:start_idx]
    dates = update.message.text[start_idx+1:end_idx].split(',')
    for i in range(len(dates)):
        multidate_event.dates.append(dates[i].strip())     

    #generate keyboard with all the dates
    keyboard = []
    subkeyboard = []
    for date in multidate_event.dates:
        if len(subkeyboard) < 3:
            subkeyboard.append(telegram.InlineKeyboardButton(text = date, callback_data = 'date:'+date))
        else:
            keyboard.append(subkeyboard)
            subkeyboard = [telegram.InlineKeyboardButton(text = date, callback_data = 'date:'+date)]

    if subkeyboard != []:
        keyboard.append(subkeyboard)

    keyboard.append([telegram.InlineKeyboardButton(text = 'OK', callback_data = 'OK')])

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    # Add everyone to unresponded and send invites to them simultaneously
    multidate_event.dict["Unresponded"] = ""
    for user in user_dictionary:
        multidate_event.dict["Unresponded"] += user + "\n"
        bot.sendMessage(chat_id = user_dictionary[user],
                        text = "You have been invited to the following event: %s\nClick on all the dates that you can make it, then click OK when you are done.\nIf you can't make it on any of the dates, just click OK."%multidate_event.info,
                        reply_markup = reply_markup)
    add_multidate_event(multidate_event)

dispatcher.add_handler(CommandHandler('multidate_event', create_event_multidate))

##
# Function that responds to button presses for single date events
# Is called whenever an inline button related to single date events was pressed by a user. These include buttons generated by /change or by the initial invitation
# Fails and informs user of failure if the event no longer exists
##
def single_event_response(bot,update):
    query = update.callback_query
    name = query.from_user.first_name
    event = get_event()

    # No event, delete all buttons and inform user 
    if event.info == '':
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                       message_id = query.message.message_id, 
                                       reply_markup = None)
        bot.sendMessage(chat_id = query.message.chat_id,
                        text = "Hmm, it seems that there isn't an event happening now.")
        return

    # First, remove the user's name from any previous attendance status, in case this function was called from /change
    event.going = event.going.replace('%s\n'%name, '')
    event.maybe = event.maybe.replace('%s\n'%name, '')

    # not going treated slightly differently due to the string also containing the reason for not going
    not_going_split = event.not_going.splitlines(True)
    for i in range(len(not_going_split)):
        not_going_split[i] = not_going_split[i].strip()
        if name in not_going_split[i]:
            not_going_split.pop(i)
            break                                
    event.not_going = string.join(not_going_split)
    
    # Handle each individual button 
    if query.data == 'single event:going':
        #remove buttons from display after they are pressed
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                   message_id = query.message.message_id, 
                                   reply_markup = None)
        event.going += '%s\n' %query.from_user.first_name
        event.unresponded = event.unresponded.replace('%s\n'%query.from_user.first_name, '')
        
        # if query.from_user.first_name in event.maybe: #for people who pressed maybe, then pressed a new button to confirm
        #     event.maybe = maybe.replace('%s\n'%query.from_user.first_name, '')

    elif query.data == 'single event:not going':
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                   message_id = query.message.message_id,  
                                   reply_markup = None)
        # if query.from_user.first_name in event.maybe:
        #     maybe = maybe.replace('%s\n'%query.from_user.first_name, '')

        bot.sendMessage(chat_id = query.message.chat_id,
                        text = "That's unfortunate, why aren't you going? "
                        "Please tell me so i can let the others know.")
        dispatcher.add_handler(reason_handler)

    elif query.data == 'single event:maybe':
        event.maybe += '%s\n' %query.from_user.first_name
        event.unresponded = event.unresponded.replace('%s\n'%query.from_user.first_name, '')
        #remove the 'maybe' button, but keep the other two 
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                   message_id = query.message.message_id, 
                                   reply_markup = telegram.InlineKeyboardMarkup([[going_button,notgoing_button]]))
        bot.sendMessage(chat_id = query.message.chat_id,
                        text = "Alright, if you can confirm, "
                        "just press either of the 'I'm Going!' or 'I can't make it' buttons, "
                        "or use /change to change your attendance status.")
    
    elif query.data == 'single event:cancel':
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                  message_id = query.message.message_id, 
                                  reply_markup = None)
        bot.editMessageText(chat_id = query.message.chat_id,
                            message_id = query.message.message_id,
                            text = '')

    #send updated list of attendees to the group
    #don't send message if not going as reason has to be given first
    if (query.data != 'single event:not going'):
        bot.sendMessage(chat_id = group_chatid,
                        text =  event.attendance())

    update_event(event)

dispatcher.add_handler(CallbackQueryHandler(single_event_response, pattern = "^single event:"))

##
# Multidate version of single_event_response
# In this case, it is called when any of the buttons containing the dates, or the OK button, is pressed
# Again, fails and informs user of failure if event no longer exists
##
def multidate_event_response(bot,update):
    print "multidate event response called"
    multidate_event = get_multidate_event()
    query = update.callback_query
    name = query.from_user.first_name
    print "dict: %s"%multidate_event.dict

    #Handle case with no event
    if multidate_event.dates == []:
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id, 
                                       message_id = query.message.message_id, 
                                       reply_markup = None)
        bot.sendMessage(chat_id = query.message.chat_id,
                        text = "Hmm, it seems that there isn't an event happening now.")
        return

    print "event detected"
    if query.data[:5] == "date:": #update database with dates that people can go
        date = query.data[5:]
        multidate_event.dict[date] += name + '\n'
        #remove button of that particular date from the inline keyboard
        subkeyboard = []
        keyboard = []
        for i in range(len(multidate_event.dates)-2):
            current_date = multidate_event.dates[i]
            if (name not in multidate_event.dict[current_date]):
                if len(subkeyboard) < 3:
                    subkeyboard.append(telegram.InlineKeyboardButton(text = current_date, callback_data = 'date:' + current_date))
                else:
                    keyboard.append(subkeyboard)
                    subkeyboard = []
                    subkeyboard.append(telegram.InlineKeyboardButton(text = current_date, callback_data = 'date:' + current_date))
        if subkeyboard != []:
            keyboard.append(subkeyboard)
        keyboard.append([telegram.InlineKeyboardButton(text = 'OK', callback_data = 'OK')])
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id,
                                   message_id = query.message.message_id,
                                   reply_markup = reply_markup)

    if query.data == 'OK': #all dates selected, send message to group
        atLeastOneDate = False
        for date in multidate_event.dict:
            if name in multidate_event.dict[date]:
                atLeastOneDate = True
        if not atLeastOneDate: #add name to nor list if no dates were selected
            multidate_event.dict["None"] += name + '\n'

        #remove name from unresponded list
        multidate_event.dict["Unresponded"] = multidate_event.dict["Unresponded"].replace('%s\n'%name,'')
      
        bot.sendMessage(chat_id = group_chatid,
                        text = multidate_event.attendance())
        bot.editMessageReplyMarkup(chat_id = query.message.chat_id,
                                   message_id = query.message.message_id,
                                   reply_markup = None)
        bot.editMessageText(chat_id = query.message.chat_id,
                            message_id = query.message.message_id,
                            text = 'Okay!')
    update_multidate_event(multidate_event)

dispatcher.add_handler(CallbackQueryHandler(multidate_event_response, pattern = "^date:|OK"))
   
    
##
# Function for user to give a reason as to why they aren't going
# Is activated when user presses the not going button
# Upon activation, it listens for a message in a private chat for the reason
# This means that it relies on the assumption that no one else would send private messages to the bot during the time where this is activated, this needs to be fixed
# It deactivates after updating the event with the reason
##
def reason(bot,update):
    event = get_event()
    if update.message.chat.type == 'private':
        reason = update.message.text
        # Detect and ignore any commands
        if reason[0] == "/":
            return
        event.not_going += "%s (%s)\n" %(update.message.from_user.first_name, reason)
        event.unresponded = event.unresponded.replace('%s\n'%update.message.from_user.first_name, '')
        dispatcher.remove_handler(reason_handler)
        #send message to group after reason is given
        bot.sendMessage(chat_id = group_chatid,
                            text =  event.attendance())
        
        update_event(event)

reason_handler = MessageHandler(Filters.text,reason)

##
# Function that allows people to change their attendance
# Handles both single and multidate events
# Is called when user types /change
##
def change(bot, update):
    event = get_event()
    multidate_event = get_multidate_event()
    dates = multidate_event.dates
    if event.info == '' and dates == []:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = 'There is currently no event.')
        return

    #single date event
    elif event.info != '': 
        name = update.message.from_user.first_name
        if update.message.chat.type == 'private':
            current_status = 'Unresponded'
            if name in event.going:
                current_status = 'Going'
            elif name in event.not_going:
                current_status = 'Not going'
            elif name in event.maybe:
                current_status = 'Maybe'
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = "Would you like to change your attendance status for %s?\n"
                                   "Your current status is %s."%(event.info,current_status),
                                   reply_markup = reply_markup_With_cancel)
            update_event(event)
            
        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = "If you wish to change your attendance status, "
                            "do so in a private chat with me.")

    #multidate event        
    elif dates != []: 
        if update.message.chat.type == 'private':
            # First remove user's name from all dates
            for date in multidate_event.dict:
                multidate_event.dict[date] = multidate_event.dict[date].replace(update.message.from_user.first_name + "\n", "")

            #Then create the keyboard and display it to the user
            keyboard = []
            subkeyboard = []
            for i in range(len(dates)-2): 
                if len(subkeyboard) < 3:
                    subkeyboard.append(telegram.InlineKeyboardButton(text = dates[i], callback_data = 'date:'+dates[i]))
                else:
                    keyboard.append(subkeyboard)
                    subkeyboard = []
                    subkeyboard.append(telegram.InlineKeyboardButton(text = dates[i], callback_data = 'date:'+dates[i]))
            if subkeyboard != []:
                keyboard.append(subkeyboard)

            keyboard.append([telegram.InlineKeyboardButton(text = 'OK', callback_data = 'OK')])
            reply_markup = telegram.InlineKeyboardMarkup(keyboard)
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = "Okay, select the new dates that you can make it, and press OK when you are done."
                            " Similarly, if you cannot make it on any of the dates, just press OK.",
                            reply_markup = reply_markup)
            update_multidate_event(multidate_event)

        else:
            bot.sendMessage(chat_id = update.message.chat_id,
                            text = "If you wish to change your attendance status, "
                            "do so in a private chat with me.")
        
dispatcher.add_handler(CommandHandler('change', change))

##
# Deletes both multidate and single date events
# Deletes both regardless of whether they exist or not
# Is called when user types /del_event
##
def del_event(bot,update):
    event = get_event()
    event.clear()
    update_event(event)

    delete_multidate_event()

    bot.sendMessage(chat_id = update.message.chat_id,
                    text = 'Event deleted!')
    
dispatcher.add_handler(CommandHandler('del_event', del_event))

##
# Gets the attendance of the current event and sends it to the user
# Is called when user types /attendance
# Handles both single and multidate events
##
def attendance(bot,update):
    print "test output"
    event = get_event()
    multidate_event = get_multidate_event()
    dates = multidate_event.dates

    if event.info != '': #single date event
        bot.sendMessage(chat_id = update.message.chat_id,
                                text = event.attendance())
    elif dates != []: #multidate event
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = multidate_event.attendance())
    else:
        bot.sendMessage(chat_id = update.message.chat_id,
                        text = "There is no event happening.")

dispatcher.add_handler(CommandHandler('attendance',attendance))    

##
# Sends a message to all users
# Called by /broadcast
##
def broadcast(bot,update):
    user_dictionary = get_user_dictionary()
    message = update.message.text[11:]
    for user in user_dictionary:
        bot.sendMessage(chat_id = user_dictionary[user],
                        text = message)

dispatcher.add_handler(CommandHandler('broadcast',broadcast))
    

   
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.setWebhook(os.environ["HEROKU_LINK"] + TOKEN)
updater.idle()


