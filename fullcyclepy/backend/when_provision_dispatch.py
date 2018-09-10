'''
#will listen to poolconfigurationchanged event and provision all known miners
#of a particular type
'''
from colorama import Fore
from helpers.antminerhelper import MinerMonitorException, stats
from helpers.queuehelper import QueueName, QueueEntries
from domain.mining import MinerAccessLevel
from backend.fcmapp import Component

PROVISION_DISPATCH = Component('provision')

def when_provisiondispatch(channel, method, properties, body):
    '''when provision event received'''
    print("[{0}] Received provision command".format(PROVISION_DISPATCH.app.now()))
    miner_type = body.decode("utf-8")
    try:
        entries = doprovisiondispatch(miner_type)
        PROVISION_DISPATCH.app.enqueue(entries)
    except Exception as ex:
        PROVISION_DISPATCH.app.logexception(ex)

def doprovisiondispatch(miner_type=None):
    '''put all miners in provision worker queue'''
    entries = QueueEntries()
    miners = PROVISION_DISPATCH.app.allminers()
    print("{0} miners configured".format(len(miners)))
    for miner in miners:
        if miner.is_disabled():
            continue
        try:
            minerstats, minerinfo, apicall, minerpool = stats(miner)
            if miner_type is not None and miner_type != '' and minerinfo.miner_type != miner_type:
                continue
            mineraccess = PROVISION_DISPATCH.app.antminer.getaccesslevel(miner)
            if mineraccess == MinerAccessLevel.Restricted:
                print(Fore.RED+"    Log: setting {0} to privileged...".format(miner.name))
                PROVISION_DISPATCH.app.antminer.set_privileged(miner)
                PROVISION_DISPATCH.app.antminer.waitforonline(miner)
                mineraccess = PROVISION_DISPATCH.app.antminer.getaccesslevel(miner)
            print(Fore.GREEN + "{0} {1} {2}".format(miner.name, minerinfo.miner_type, mineraccess))
            if mineraccess == MinerAccessLevel.Restricted:
                print("    skipping restricted access")
            else:
                entries.add(QueueName.Q_PROVISION, PROVISION_DISPATCH.app.messageencode(miner))
        except MinerMonitorException as minerex:
            print(minerex)
        except BaseException as ex:
            print('while provisioning {0} ({1})'.format(miner.ipaddress, miner.key()))
            print(PROVISION_DISPATCH.app.exceptionmessage(ex))
    return entries

def main():
    if PROVISION_DISPATCH.app.isrunnow or PROVISION_DISPATCH.app.isdebug:
        entries = doprovisiondispatch()
        PROVISION_DISPATCH.app.enqueue(entries)
        PROVISION_DISPATCH.app.shutdown()
    else:
        PROVISION_DISPATCH.listeningqueue = PROVISION_DISPATCH.app.subscribe(QueueName.Q_POOLCONFIGURATIONCHANGED, when_provisiondispatch)
        PROVISION_DISPATCH.listen()

if __name__ == "__main__":
    main()
