'''#domain services layer'''

#operations are use cases

def poolstoadd(miner, minerpool, poollist):
    '''find pools that miner does not have'''
    poolsneeded = []
    #loop through pools for miner type
    for pool in poollist:
        if pool.pool_type == miner.minerinfo.miner_type and pool.url is not None and pool.url != "":
            foundpool = None
            jpools = minerpool.allpools["POOLS"]
            for existingpool in jpools:
                if pool.url == existingpool["URL"] and existingpool["User"].startswith(pool.user):
                    foundpool = existingpool
            #if miner does not have pool configured
            if foundpool is None:
                poolsneeded.append(pool)
    return poolsneeded
