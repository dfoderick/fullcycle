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

class DiscoveryResults:
    def __init__(self):
        self.minerstotal = 0
        self.minersnew = 0
        self.shownonminers = True
        self.hostsup = 0
        self.entries = QueueEntries()
        self.knownminers = None
        self.hosts_list = None

    def process_miner(self, miner, status):
        minerstats, minerinfo, apicall, minerpool = antminerhelper.stats(miner)
        miner.setminerinfo(minerinfo)
        if minerinfo.miner_type:
            self.minerstotal += 1
            if not self.shownonminers:
                print("{0} {1} {2}".format(miner.ipaddress, status, miner.networkid))
            print(Fore.GREEN + '   found {0} with id {1}'.format(minerinfo.miner_type, minerinfo.minerid))
            #find by mac address or miner_id, not name
            found = None
            #if miner.minerid != "unknown"
            for known in self.knownminers:
                if known.networkid == miner.networkid or (not miner.is_unknown and known.minerid == miner.minerid):
                    found = known
            if found:
                print(Fore.YELLOW + '   already know about {0}'.format(found.name))
            else:
                self.minersnew += 1
                self.entries.add(QueueName.Q_DISCOVERED, DISCOVER.app.messageencode(miner))
                print(Fore.GREEN + '   discovered {0}'.format(miner.name))

    def print(self):
        print('nmap queried {0} hosts on network'.format(len(self.hosts_list)))
        print('{0} hosts are up'.format(self.hostsup))
        print('FCM knows about {0} miners configured'.format(len(self.knownminers)))
        print('FCM determined {0} miners this attempt'.format(self.minerstotal))
        print('FCM determined there are {0} new miners on network'.format(self.minersnew))


DISCOVER = Component('discover')
MINERPORT = DISCOVER.app.configuration.get('discover.minerport')
SSHPORT = DISCOVER.app.configuration.get('discover.sshport')
DNS = DISCOVER.app.configuration.get('discover.dns')

def findminers(hosts_list, knownminers):
    '''find miners on network'''
    discovery = DiscoveryResults()
    discovery.knownminers = knownminers
    discovery.hosts_list = hosts_list
    print('Querying {0} hosts...'.format(len(hosts_list)))
    for host, status, macaddress in hosts_list:
        try:
            if status != 'down':
                discovery.hostsup += 1
                if discovery.shownonminers:
                    print("{0} {1} {2}".format(host, status, macaddress))
                miner = mining.Miner(name=host, ipaddress=host, port=MINERPORT, ftpport='', networkid=macaddress)
                try:
                    discovery.process_miner(miner, status)

                except antminerhelper.MinerMonitorException as monitorex:
                    try:
                        if monitorex.istimedout:
                            if discovery.shownonminers:
                                print(Fore.RED + '    Not a miner')
                    except Exception:
                        DISCOVER.app.logexception(monitorex)
                except BaseException as baseex:
                    print(Fore.RED + DISCOVER.app.exceptionmessage(baseex))
        except KeyboardInterrupt:
            break
    discovery.print()
    return discovery.entries

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
