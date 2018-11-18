#!/usr/bin/env python
# -*- coding: utf-8 -*-



from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
import urllib
from urllib.request import urlopen
import webbrowser
import json
import requests
import re
from html.parser import HTMLParser
import os , errno

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BASE_LYRICS_URL = 'http://lyric-api.herokuapp.com/api/find/'
SLASH = '/'
LYRICS_ERROR_MSG = 'Lyrics not found. use /help for more info.'
LYRICS_WAITING_MSG = 'Looking up lyrics for the song you requested. Please wait.'
USAGE_MSG = 'Usage: Song name - Artist (Ex : Lose Yourself - hey)'
BOT_TAG = '\n\n[Looking for more lyrics?](https://telegram.me/engLyricsFinderbot)'
USER_TAG = '@engLyricsFinderbot'

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
def correct(nameOrg):
            # grab html
            name = urllib.parse.quote_plus(nameOrg)
            html = get_page('http://www.google.com/search?hl=en&q=' + name + '&meta=&gws_rd=ssl')
            logger.info('name: %s, nameOrg: %s ',name,nameOrg)

            
            html_parser = HTMLParser()

            # save html for debugging
            # open('page.html', 'w').write(html)

            # pull pieces out
            match = re.search(r'(?:Showing results for|Did you mean|Including results for)[^\0]*?<a.*?>(.*?)</a>', html)
            if match:
                if len(match.group(1)) > 250:
                        fix = nameOrg
                else:
                        fix = match.group(1)
                        fix = re.sub(r'<.*?>', '', fix)
                        fix = html_parser.unescape(fix)

            # return result
            #print (fix)
            return fix

def get_page(url):
            # the type of header affects the type of response google returns
            # for example, using the commented out header below google does not 
            # include "Including results for" results and gives back a different set of results
            # than using the updated user_agent yanked from chrome's headers
            # user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'
            headers = {'User-Agent':user_agent,}
            req = urllib.request.Request(url, None, headers)
            page = urllib.request.urlopen(req)
            html = str(page.read())
            page.close()
            return html

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(USAGE_MSG)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(USAGE_MSG)

def lyricsCmd(bot, update,args):
    """For using the bot in groups with /lyrics command"""
    print ('I\'m here')
    searchName = ' '.join(args)
    update.message.text=searchName
    print (update.message.text)
    lyrics(bot,update)

    
def lyrics(bot, update):
    
    searchQuery = update.message.text
    #print (searchQuery)
    #searchQuery = urllib.parse.quote_plus(searchQuery)
    #print (searchQuery)
    searchQuery = correct(searchQuery)
    #print (searchQuery)
    #update.message.reply_text(searchQuery)
    #print (update.effective_user)
    #print(update.effective_user.first_name)
    
    
    logger.info('%s(%s) with userid: %s is looking for %s',update.effective_user.first_name,update.effective_user.username,str(update.effective_user.id),searchQuery)
    
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
            logger.info('Lyrics not found.')
            update.message.reply_text(LYRICS_ERROR_MSG)
        else :
            lyrics = data['lyric']
            #print (lyrics)
            if len(lyrics) < 4000:
                #print(len(lyrics))
                #print(len(BOT_TAG))
                update.message.reply_text(lyrics+BOT_TAG,parse_mode=ParseMode.MARKDOWN)
            else:
                #print(len(lyrics))
                update.message.reply_text('lyrics length exceeds Telegram\'s message length limitaions.\nSending a file instead...')
                fileName = songName.replace('%20','-') +'.txt'
                with open(fileName, "w") as text_file:
                    print(lyrics, file=text_file)
                update.message.reply_document(document=open(fileName, 'rb'),caption=BOT_TAG+'\n'+USER_TAG,parse_mode=ParseMode.MARKDOWN)
                silentremove(fileName)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: songname - artist name')
        logger.warning('Update "%s" caused error, update')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("572076500:AAGBEQig_qcNY1gL0mjMH0pEKS1OU8KBOcI")
    #updater = Updater("564292532:AAHyKNyLC69zyEMOtGAEDi5TaE1IeM_gaMo")
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("lyrics", lyricsCmd, pass_args=True))
    
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