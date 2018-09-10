'''Repository'''
import json
from domain.mining import Miner

class MinerRepository(object):
    """repository for miners"""

    def readminers(self, file_name):
        with open(file_name, encoding='utf-8-sig') as config_file:
            jsonarray = json.loads(config_file.read())
        miners = [Miner(**k) for k in jsonarray]
        #TODO: Remove disabled miners
        #if miner.name.startswith("#"):
        return miners

    def activeminers(self, file_name):
        for miner in self.readminers(file_name):
            if miner.is_disabled() is False: yield miner
