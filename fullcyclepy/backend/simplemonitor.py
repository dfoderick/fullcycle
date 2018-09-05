'''gets stats from a miner and serializes to disk'''
import time
import asyncio
from colorama import Fore
from helpers import antminerhelper
from fcmapp import ApplicationService
from domain.mining import MinerApiCall
from concurrent.futures import ThreadPoolExecutor

# call all the api command of miner

#async def getstats_async(miner):
#    minerstats, minerinfo, statspolling, minerpool = await antminerhelper.stats(miner)
#    return minerstats, minerinfo, statspolling, minerpool

def getstats(miner):
    minerstats, minerinfo, statspolling, minerpool = antminerhelper.stats(miner)
    return miner, minerstats, minerinfo, statspolling, minerpool


def process_results(results):
    for miner, minerstats, minerinfo, statspolling, minerpool in results:
        if minerstats is None:
            APP.logerror('{0} Offline? {1}'.format(miner.name, miner.ipaddress))
        else:
            savedminer = APP.getminer(miner)
            if not savedminer:
                print('Could not find saved miner {0}'.format(miner.name))
                savedminer = miner
            poolname = '{0} {1}'.format(minerpool.currentpool, minerpool.currentworker)
            foundpool = APP.findpool(minerpool)
            if foundpool is not None:
                minerpool.poolname = foundpool.name
            savedminer.monitored(minerstats, minerpool, minerinfo, statspolling.elapsed())
            print('{0} mining at {1}({2})'.format(savedminer.name, minerpool.poolname, poolname))

            print(Fore.CYAN + str(APP.now()), miner.name, miner.status,
                    str(minerstats.currenthash), str(minerstats.minercount),
                    'temp=' + str(minerstats.tempboardmax()),
                    savedminer.uptime(minerstats.elapsed),
                    '{0:d}ms'.format(int(savedminer.monitorresponsetime() * 1000)))

            ##switches miner to default pool
            #if miner.defaultpool:
            #    founddefault = next((p for p in POOLS if p.name == miner.defaultpool), None)
            #    if founddefault is not None:
            #        #minerpool = antminerhelper.pools(miner)
            #        if minerpool is not None:
            #            #find pool number of default pool and switch to it
            #            switchtopoolnumber = minerpool.findpoolnumberforpool(founddefault.url, founddefault.user)
            #            if switchtopoolnumber is not None and switchtopoolnumber > 0:
            #                antminerhelper.switch(miner, switchtopoolnumber)
            #                print(Fore.YELLOW + str(APP.now()), miner.name, 'switched to', miner.defaultpool)

        #APP.putminerandstats(savedminer, minerstats, minerpool)
        #APP.updateknownminer(savedminer)

def getminers(MINERS):
    listofminers=[]
    cnt = 300
    while cnt>0:
        for miner in MINERS:
            listofminers.append(miner)
        cnt -= 1
    return listofminers

async def run_tasks(executor, MINERS):
    listofminers = getminers(MINERS)
    calltime = MinerApiCall(None)
    calltime.start()

    loop = asyncio.get_event_loop()
    #tasks = [asyncio.ensure_future(getstats_async(miner)) for miner in getminers()]
    #results = loop.run_in_executor(executor, asyncio.gather(*tasks))
    #futures = loop.run_in_executor(executor, getstats, *getminers(MINERS))
    tasks = [loop.run_in_executor(executor, getstats, miner) for miner in listofminers]
    completed, pending = await asyncio.wait(tasks)
    results = [t.result() for t in completed]
    calltime.stop()

    totalms = int(calltime.elapsed()*1000)
    print('{0} in {1}ms. Avg={2}ms'.format(len(listofminers), totalms, totalms/len(listofminers)))

    process_results(results)

if __name__ == '__main__':
    print('Starting...')
    APP = ApplicationService(component='fullcycle')
    APP.print('started app. getting known miners')
    MINERS = APP.miners()
    APP.print("{0} miners configured".format(len(MINERS)))

    #POOLS = APP.pools()
    executor = ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_tasks(executor, MINERS))
    loop.close()
    APP.shutdown()
    WHATISAID = input('done')
