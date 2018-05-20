'''what to do when an alert is triggered'''
from helpers.queuehelper import QueueName
from fcmapp import Component

ALERT = Component('alert')

def when_alert(channel, method, properties, body):
    '''when alert is fired'''
    try:
        print("[{0}] Received request to send telegram".format(ALERT.app.now()))
        doalert(body.decode())
    except Exception as ex:
        ALERT.app.logexception(ex)

def doalert(alertmsg):
    '''send the alert'''
    ALERT.app.sendtelegrammessage(alertmsg)
    print("Sent telegram {0}".format(alertmsg))

def main():
    ALERT.listeningqueue = ALERT.app.listen_to_broadcast(QueueName.Q_ALERT, when_alert)

if __name__ == "__main__":
    main()
