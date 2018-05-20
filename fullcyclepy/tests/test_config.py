'''test writing to config file'''
import json
from marshmallow import pprint
from domain.mining import Pool
from domain.rep import PoolRepository
from messaging.schema import PoolSchema
from backend.fcmapp import Component

sch = PoolSchema()
pools = PoolRepository()
savedpools = pools.readpools("backend/config/pools.conf")

pool1 = Pool('Antminer 1', 'Name 1', 'http://url1','user1.',1)
#pools.add(pool1,PoolSchema())
pool2 = Pool('Antminer 2', 'Name 2', 'http://url2','user2.',2)
#pools.add(pool2,PoolSchema())
savedpools.append(pool1)
savedpools.append(pool2)

#savedpools = pools.readpools()
#for pool in savedpools:
#    print(pool.__dict__)

jsonpools = [sch.dump(k).data for k in savedpools]

s = json.dumps(jsonpools, sort_keys = True, indent = 4, ensure_ascii = False)
print(s)
input('any key')
