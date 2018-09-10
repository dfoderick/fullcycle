'''logs message to terminal. in future may log to database'''
from helpers.queuehelper import QueueName
from backend.fcmapp import Component

COMPONENTLOG = Component('log')

def when_log(channel, method, properties, body):
    '''event handler when log event is raised'''
    try:
        print("[{0}] Received log message".format(COMPONENTLOG.app.now()))
        dolog(body.decode())
    except Exception as ex:
        COMPONENTLOG.app.logexception(ex)

def dolog(msg):
    print(msg)

def main():
    COMPONENTLOG.listeningqueue = COMPONENTLOG.app.listen_to_broadcast(QueueName.Q_LOG, when_log)

if __name__ == "__main__":
    main()
