'''#what to do when miner is offline?
#maybe send alert?
#maybe disable the miner after a while?
'''
from helpers.queuehelper import QueueName, QueueEntries
from domain import mining
from fcmapp import Component

OFFLINE = Component('offline')

def when_offline(channel, method, properties, body):
    '''when miner goes offline'''
    print("[{0}] Received miner offline message".format(OFFLINE.app.now()))
    try:
        entries = dooffline(OFFLINE.app.messagedecodeminer(body))
        OFFLINE.app.enqueue(entries)
    except Exception as ex:
        OFFLINE.app.logexception(ex)

def dooffline(miner: mining.Miner):
    '''notify user'''
    entries = QueueEntries()
    savedminer = OFFLINE.app.getminer(miner)
    if not savedminer.is_disabled():
        if savedminer.is_send_offline_alert():
            #update status to offline and alert
            savedminer.status = mining.MinerStatus.Offline
            alertmsg = 'miner {0} is offline! since...'.format(savedminer.name)
            OFFLINE.app.putminer(savedminer)
            entries.addalert(alertmsg)
            print("Sent offline alert '{0}'".format(alertmsg))
        else:
            #stop annoying the user, disable the miner to stop sending alerts
            savedminer.status = mining.MinerStatus.Disabled
            alertmsg = 'miner {0} is Disabled after many offline alerts. No more alerts will be sent for this miner.'.format(savedminer.name)
            OFFLINE.app.putminer(savedminer)
            entries.addalert(alertmsg)
            print("Sent disabled alert for {0}".format(savedminer.name))
    else:
        if not savedminer.is_manually_disabled():
            print('Disabled miner {0} is offline. manually disable miner to get rid of this message'.format(miner.name))

    return entries

def main():
    OFFLINE.listeningqueue = OFFLINE.app.subscribe_and_listen(QueueName.Q_OFFLINE, when_offline)

if __name__ == "__main__":
    main()
