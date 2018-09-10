'''# Scans network to see if there are new miners
# Listens for Discover
# Raises Discovered event
# TODO: check if found miner is in miners.json and add it if not
'''
from colorama import Fore
from helpers.networkhelper import networkmap
from helpers import antminerhelper
from helpers.queuehelper import QueueName, QueueEntries
from domain import mining
from backend.fcmapp import Component

DISCOVER = Component('discover')
MINERPORT = DISCOVER.app.configuration('discover.minerport')
SSHPORT = DISCOVER.app.configuration('discover.sshport')
DNS = DISCOVER.app.configuration('discover.dns')

def findminers(hosts_list, knownminers):
    '''find miners on network'''
    entries = QueueEntries()
    minerstotal = 0
    minersnew = 0
    shownonminers = True
    hostsup = 0
    print('Querying {0} hosts...'.format(len(hosts_list)))
    for host, status, macaddress in hosts_list:
        try:
            if status != 'down':
                hostsup += 1
                if shownonminers:
                    print("{0} {1} {2}".format(host, status, macaddress))
                miner = mining.Miner(name=host, ipaddress=host, port=MINERPORT, ftpport='', networkid=macaddress)
                try:
                    minerstats, minerinfo, apicall, minerpool = antminerhelper.stats(miner)
                    miner.setminerinfo(minerinfo)
                    if minerinfo.miner_type:
                        minerstotal += 1
                        if not shownonminers:
                            print("{0} {1} {2}".format(host, status, macaddress))
                        print(Fore.GREEN + '   found {0} with id {1}'.format(minerinfo.miner_type, minerinfo.minerid))
                        #find by mac address or miner_id, not name
                        found = None
                        #if miner.minerid != "unknown"
                        for known in knownminers:
                            if known.networkid == miner.networkid or (miner.minerid != "unknown" and known.minerid == miner.minerid):
                                found = known
                        if found:
                            print(Fore.YELLOW + '   already know about {0}'.format(found.name))
                        else:
                            minersnew += 1
                            entries.add(QueueName.Q_DISCOVERED, DISCOVER.app.messageencode(miner))
                            print(Fore.GREEN + '   discovered {0}'.format(miner.name))

                except antminerhelper.MinerMonitorException as monitorex:
                    try:
                        if monitorex.istimedout:
                            if shownonminers:
                                print(Fore.RED + '    Not a miner')
                    except Exception:
                        DISCOVER.app.logexception(monitorex)
                except BaseException as baseex:
                    print(Fore.RED + DISCOVER.app.exceptionmessage(baseex))
        except KeyboardInterrupt:
            break
    print('nmap queried {0} hosts on network'.format(len(hosts_list)))
    print('{0} hosts are up'.format(hostsup))
    print('FCM knows about {0} miners configured'.format(len(knownminers)))
    print('FCM determined {0} miners this attempt'.format(minerstotal))
    print('FCM determined there are {0} new miners on network'.format(minersnew))
    return entries

def when_discover(channel, method, properties, body):
    '''when miner need to be discovered'''
    print("[{0}] Received discover command".format(DISCOVER.app.now()))
    try:
        dodiscover()
    except Exception as ex:
        DISCOVER.app.logexception(ex)

def dodiscover():
    '''find miners on network'''
    hosts_list = networkmap(DNS, MINERPORT, SSHPORT)
    entries = findminers(hosts_list, DISCOVER.app.knownminers())
    DISCOVER.app.enqueue(entries)

def main():
    '''main'''
    if DISCOVER.app.isrunnow:
        dodiscover()
        DISCOVER.app.shutdown()
    else:
        DISCOVER.listeningqueue = DISCOVER.app.subscribe(QueueName.Q_DISCOVER, when_discover)
        DISCOVER.listen()

if __name__ == "__main__":
    main()
