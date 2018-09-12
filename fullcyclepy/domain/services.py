'''#domain services layer'''

#operations are use cases

def poolstoadd(miner, minerpool, poollist):
    '''find pools that miner does not have'''
    poolsneeded = []
    #loop through pools for miner type
    for pool in poollist:
        if miner.minerinfo.miner_type.startswith(pool.pool_type) and pool.url is not None and pool.url != "":
            #if miner does not have pool configured
            foundpool = findpool(minerpool, pool)
            if foundpool is None:
                poolsneeded.append(pool)
    return poolsneeded

def findpool(minerpool, pool):
    foundpool = None
    jpools = minerpool.allpools["POOLS"]
    for existingpool in jpools:
        if pool.url == existingpool["URL"] and existingpool["User"].startswith(pool.user):
            foundpool = existingpool
    return foundpool
