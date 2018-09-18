'''test writing to config file'''
import json
from marshmallow import pprint
from domain.mining import Pool
from domain.rep import PoolRepository
from messaging.schema import PoolSchema

SCH = PoolSchema()
POOLS = PoolRepository()
SAVEDPOOLS = POOLS.readpools("backend/config/pools.conf")

POOL1 = Pool('Antminer 1', 'Name 1', 'http://url1', 'user1.', 1)
#pools.add(pool1,PoolSchema())
POOL2 = Pool('Antminer 2', 'Name 2', 'http://url2', 'user2.', 2)
#pools.add(pool2,PoolSchema())
SAVEDPOOLS.append(POOL1)
SAVEDPOOLS.append(POOL2)

JSON_POOLS = [SCH.dump(k).data for k in SAVEDPOOLS]

FORMATTED_JSON = json.dumps(JSON_POOLS, sort_keys=True, indent=4, ensure_ascii=False)
pprint(FORMATTED_JSON)
#input('func_config: any key')
