'''telegram api'''
import datetime
from telethon import TelegramClient

def sendalert(message, service):
    '''send the message'''
    print("telegramhelper.py:{0}{1}".format(str(datetime.datetime.now()), message))
    api_id = service.user
    api_hash = service.password
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    client.send_message(service.connection, message)
    client.disconnect()

def sendfile(file, service):
    '''send the message'''
    print("telegramhelper.py:{0}{1}".format(str(datetime.datetime.now()), file))
    api_id = service.user
    api_hash = service.password
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    client.send_file(service.connection, file)
    client.disconnect()
