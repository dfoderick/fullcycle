'''serialization schema'''
from marshmallow import Schema, fields, post_load
import domain.minerstatistics
from domain.mining import MinerInfo, MinerCurrentPool, Miner, Pool, MinerCommand, AvailablePool

class MinerInfoSchema(Schema):
    '''schema for miner information'''
    miner_type = fields.Str()
    minerid = fields.Str()

    @post_load
    def make(self, data):
        return MinerInfo(**data)

class MinerCurrentPoolSchema(Schema):
    '''schema for current pool'''
    poolname = fields.Str()
    currentpool = fields.Str()
    currentworker = fields.Str()
    #allpools is a json dict or None
    allpools = fields.Dict()

    @post_load
    def make(self, data):
        onlyparams = {x: data[x] for x in data if x not in {'poolname'}}
        minerpool = MinerCurrentPool(miner=None, **onlyparams)
        if 'poolname' in data:
            minerpool.poolname = data['poolname']
        return minerpool

class MinerStatsSchema(Schema):
    '''schema for statistics'''
    when = fields.DateTime()
    minercount = fields.Str()
    currenthash = fields.Int()
    controllertemp = fields.Int()
    tempboard1 = fields.Int()
    tempboard2 = fields.Int()
    tempboard3 = fields.Int()
    boardstatus1 = fields.Str(allow_none=True)
    boardstatus2 = fields.Str(allow_none=True)
    boardstatus3 = fields.Str(allow_none=True)
    elapsed = fields.Int()
    fan1 = fields.Str()
    fan2 = fields.Str()
    fan3 = fields.Str()
    frequency = fields.Str(allow_none=True)
    rawstats = fields.Dict(allow_none=True)

    @post_load
    def make(self, data):
        return domain.minerstatistics.MinerStatistics(miner=None, **data)

class MinerSchema(Schema):
    '''schema for a miner'''
    name = fields.Str()
    status = fields.Str(allow_none=True)
    laststatuschanged = fields.DateTime(allow_none=True)
    miner_type = fields.Str()
    ipaddress = fields.Str()
    port = fields.Str()
    ftpport = fields.Str()
    username = fields.Str()
    password = fields.Str()
    clientid = fields.Str()
    networkid = fields.Str()
    minerid = fields.Str()
    lastmonitor = fields.DateTime(allow_none=True)
    offlinecount = fields.Int()
    minerinfo = fields.Nested(MinerInfoSchema, allow_none=True)
    minerpool = fields.Nested(MinerCurrentPoolSchema, allow_none=True)
    minerstats = fields.Nested(MinerStatsSchema, allow_none=True)
    location = fields.Str(allow_none=True)
    in_service_date = fields.DateTime(allow_none=True)

    @post_load
    def make(self, data):
        return Miner(**data)

class MinersSchema(Schema):
    '''schema for list of miner'''
    miners = fields.Nested(MinerSchema)

class MinerCommandSchema(Schema):
    '''schema for miner commands'''
    command = fields.Str()
    parameter = fields.Str()

    @post_load
    def make_command(self, data):
        return MinerCommand(**data)

class PoolSchema(Schema):
    pool_type = fields.Str()
    name = fields.Str()
    url = fields.Str()
    user = fields.Str()
    password = fields.Str()
    priority = fields.Int()
    password = fields.Str()

    @post_load
    def make(self, data):
        return Pool(**data)


class AvailablePoolSchema(Schema):
    '''schema for available pool'''
    pool_type = fields.Str()
    named_pool = fields.Nested(PoolSchema, allow_none=True)
    url = fields.Str(allow_none=True)
    user = fields.Str(allow_none=True)
    password = fields.Str(required=False)
    priority = fields.Int(allow_none=True)

    @post_load
    def make(self, data):
        return AvailablePool(**data)
