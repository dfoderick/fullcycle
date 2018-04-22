'''serialization schema'''
from marshmallow import Schema, fields, post_load
#from messaging.messages import *
from domain.mining import MinerInfo, MinerCurrentPool, MinerStatistics, Miner, MinerCommand

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
    elapsed = fields.Int()
    fan1 = fields.Str()
    fan2 = fields.Str()
    fan3 = fields.Str()

    @post_load
    def make(self, data):
        return MinerStatistics(miner=None, **data)

class MinerSchema(Schema):
    '''schema for a miner'''
    name = fields.Str()
    status = fields.Str()
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

#class EventSchema(Schema):
#    """Event? """
#    todo = fields.Str()
