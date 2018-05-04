'''telegram api'''
import datetime
from telegram import Bot

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def sendalert(message, service):
    '''send the message'''
    print("telegramhelper.py:{0} {1}".format(str(datetime.datetime.now()), message))
    chat_id = service.user
    bot = Bot(token=service.password)
    bot.send_message(chat_id=chat_id, text=message)

def sendphoto(file, service):
    '''send the photo'''
    print("telegramhelper.py:{0} {1}".format(str(datetime.datetime.now()), file))
    chat_id = service.user
    bot = Bot(token=service.password)
    bot.send_photo(chat_id, photo=open(file, 'rb'))
