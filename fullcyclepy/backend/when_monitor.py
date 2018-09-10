'''David Foderick, Skylake Software Inc.
'''
#from helpers import antminerhelper
from helpers.queuehelper import QueueName, QueueEntries
from backend.fcmapp import Component

MONITOR = Component('monitor')

def when_monitor(channel, method, properties, body):
    '''when its time to monitor all the machines on schedule'''
    try:
        print("[{0}] Received monitor command".format(MONITOR.app.now()))
        entries = domonitor()
        MONITOR.app.enqueue(entries)
    except Exception as ex:
        MONITOR.app.logexception(ex)

def domonitor():
    '''queue workers to run the individual miner monitoring'''
    entries = QueueEntries()
    try:
        miners = MONITOR.app.allminers()
        print("{0} miners configured".format(len(miners)))

        for miner in miners:
            if not miner.is_manually_disabled():
                entries.add(QueueName.Q_MONITORMINER, MONITOR.app.messageencode(miner))
        print("waiting for next monitor event")
    except Exception as theex:
        MONITOR.app.logexception(theex)
    return entries

def main():
    if MONITOR.app.isrunnow or MONITOR.app.isdebug:
        domonitor()
        MONITOR.app.shutdown()
    else:
        MONITOR.listeningqueue = MONITOR.app.subscribe(QueueName.Q_MONITOR, when_monitor)
        MONITOR.app.listen(MONITOR.listeningqueue)

if __name__ == "__main__":
    main()
