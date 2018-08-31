'''gets stats from a miner and serializes to disk'''
import time
from colorama import Fore
from helpers import antminerhelper
from fcmapp import ApplicationService

# call all the api command of miner

APP = ApplicationService(component='fullcycle')

MINERS = APP.knownminers()
print("{0} miners configured".format(len(MINERS)))

POOLS = APP.pools()

for miner in MINERS:
    try:
        savedminer = APP.getminer(miner)
        if not miner.is_manually_disabled():
            minerpool = None
            start = time.perf_counter()
            minerinfo = antminerhelper.getminerinfo(miner)
            minerstats = antminerhelper.stats(miner)
            #minerlcd = antminerhelper.getminerlcd(miner)
            if minerstats is None:
                APP.logerror('{0} Offline? {1}'.format(miner.name, miner.ipaddress))
            else:
                minerpool = antminerhelper.pools(miner)
                end = time.perf_counter()
                monitorperf = end - start
                poolname = '{0} {1}'.format(minerpool.currentpool, minerpool.currentworker)
                foundpool = APP.findpool(minerpool)
                if foundpool is not None:
                    minerpool.poolname = foundpool.name
                savedminer.monitored(minerstats, minerpool, minerinfo, monitorperf)
                print('{0} mining at {1}'.format(savedminer.name, minerpool.poolname))

                print(Fore.CYAN + str(APP.now()), miner.name, miner.status,
                      str(minerstats.currenthash), str(minerstats.minercount),
                      'temp=' + str(minerstats.tempboardmax()),
                      savedminer.uptime(minerstats.elapsed),
                      '{0:0f}ms'.format(savedminer.monitorresponsetime() * 1000))

                #switches miner to default pool
                if miner.defaultpool:
                    founddefault = next((p for p in POOLS if p.name == miner.defaultpool), None)
                    if founddefault is not None:
                        minerpool = antminerhelper.pools(miner)
                        if minerpool is not None:
                            #find pool number of default pool and switch to it
                            switchtopoolnumber = minerpool.findpoolnumberforpool(founddefault.url, founddefault.user)
                            if switchtopoolnumber is not None and switchtopoolnumber > 0:
                                antminerhelper.switch(miner, switchtopoolnumber)
                                print(Fore.YELLOW + str(APP.now()), miner.name, 'switched to', miner.defaultpool)

            APP.putminerandstats(savedminer, minerstats, minerpool)
            APP.updateknownminer(savedminer)
    except Exception as ex:
        print(Fore.RED + 'Error on {0}'.format(miner.name))
        APP.logexception(ex)

APP.shutdown()
WHATISAID = input('done')
