'''a component that gathers stats and hearbeats from other components
evaluate if this is going to be used or not
'''

from helpers.queuehelper import QueueName
from backend.fcmapp import ApplicationService

APP = ApplicationService(component='component')

def when_component(channel, method, properties, body):
    '''when the event happens'''
    try:
        print("[{0}] Received component message".format(APP.now()))
        docomponent(body.decode())
    except Exception as ex:
        APP.logexception(ex)

def docomponent(msg):
    '''do this'''
    APP.sendtelegrammessage(msg)
    print("Sent telegram {0}".format(msg))

Q = APP.subscribe(QueueName.Q_COMPONENT, when_component)
APP.bus.listen(Q)
