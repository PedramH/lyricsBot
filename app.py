#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import urllib
#import urllib2
from urllib.request import urlopen
import webbrowser
import json
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BASE_LYRICS_URL = 'http://lyric-api.herokuapp.com/api/find/'
SLASH = '/'
LYRICS_ERROR_MSG = 'Lyrics not found. use /help for more info.'
LYRICS_WAITING_MSG = 'Looking up lyrics for the song you requested. Please wait.'
USAGE_MSG = 'Usage: Song name - Artist (Ex : Lose Yourself - Eminem)'



# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(USAGE_MSG)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(USAGE_MSG)
    
def lyrics(bot, update):
    
    searchQuery = update.message.text
   # update.message.reply_text(searchQuery)
    
    try:
        sp=searchQuery.split("-")
        
        songName=sp[0]
        songName=songName.lower()
        songName = songName.strip()
        #update.message.reply_text(songName)
        
        artistName=sp[1]
        artistName=artistName.lower()
        artistName = artistName.strip()
        #update.message.reply_text(artistName)
        msg = 'Looking up lyrics for ' + songName +' By ' + artistName + ' ...' 
        update.message.reply_text(msg)
        
        artistName = artistName.replace(' ', '%20')
        songName = songName.replace(' ', '%20')
        
        LYRICS_URL = BASE_LYRICS_URL + artistName + SLASH + songName
        response = requests.get(LYRICS_URL)
        data = response.json()
        if data['lyric'] == '' :
            print ('Lyrics not found.')
            update.message.reply_text(LYRICS_ERROR_MSG)
        else :
            lyrics = data['lyric']
            #print (lyrics)
            update.message.reply_text(lyrics)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: songname - artist name')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("564292532:AAH7H7-9AujaPN9twCc1V4ggdVpvK5Btzq4")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, lyrics))
    

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()