#import time
import json

def safestring(thestring):
    '''safely convert anything into string'''
    if thestring is None:
        return None
    if isinstance(thestring, str): return thestring
    return str(thestring, "utf-8")

def formattime(the_time):
    '''standard format for time'''
    return the_time.strftime('%Y-%m-%d %H:%M:%S')

def jsonserialize(sch, msg):
    '''serialize a message with schema. returns string'''
    smessage = sch.dumps(msg)
    #json.dumps(jmessage)
    return smessage.data

def deserialize(sch, msg):
    '''Output should be entity, not python json object
    msg parameter should be string
    '''
    if msg is None: return None
    return sch.loads(msg).data

def deserializelist_withschema(schema, the_list):
    '''deserialize list of strings into entities'''
    results = []
    for item in the_list:
        entity = deserialize(schema, safestring(item))
        #todo:for pools the entry is a list
        results.append(entity)
    return results

def serialize(entity, schema):
    return schema.dumps(entity).data

def serializelist(listofentities):
    '''serialize a list of entities'''
    json_list = json.dumps([e.__dict__ for e in listofentities])
    return json_list

def deserializelistofstrings(the_list, sch):
    '''deserialize list of strings into list of miners'''
    results = []
    for item in the_list:
        miner = deserialize(sch, safestring(item))
        results.append(miner)
    return results
