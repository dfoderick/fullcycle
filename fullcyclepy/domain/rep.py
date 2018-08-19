'''Repositories'''
import json
import domain.mining
import domain.miningrules

class BaseRepository(object):
    def readrawfile(self, file_name):
        with open(file_name, encoding='utf-8-sig') as config_file:
            raw = config_file.read()
        return raw


class MinerRepository(BaseRepository):
    def readminers(self, file_name):
        '''read miners'''
        raw = self.readrawfile(file_name)
        miners = [domain.mining.Miner(**k) for k in json.loads(raw)]
        #TODO: Remove disabled miners
        #if miner.name.startswith("#"):
        return miners

    def getminerbyname(self, minername, file_name):
        '''get miner by name'''
        miners = self.readminers(file_name)
        for miner in miners:
            if miner.name == minername:
                return miner
        return None

class PoolRepository(BaseRepository):
    def readpools(self, file_name):
        raw = self.readrawfile(file_name)
        poollist = [domain.mining.Pool(**k) for k in json.loads(raw)]
        #TODO:Remove disabled pools
        return poollist

    def add(self, pool, file_name, sch):
        pools = self.readpools(file_name)
        if not any(x.name == pool.name for x in pools):
            pools.append(pool)

        jsonpools = [sch.dump(k).data for k in pools]
        with open(file_name, 'w') as file:
            json.dump(jsonpools, file, sort_keys=True, indent=4, ensure_ascii=False)


class LoginRepository(object):
    '''login repository'''
    def readlogins(self, file_name):
        '''get entity from config'''
        with open(file_name, encoding='utf-8-sig') as config_file:
            jlogin = json.loads(config_file.read())
        login = domain.mining.Login(jlogin['username'], jlogin['password'])
        return login

    def getsshlogin(self, miner):
        '''TODO: make login per miner'''
        return self.readlogins('config/ftp.conf')

class RuleParametersRepository(BaseRepository):
    def readrules(self, file_name):
        raw = self.readrawfile(file_name)
        ruleslist = [domain.miningrules.RuleParameters(**k) for k in json.loads(raw)]
        return ruleslist

class MinerTypeRepository(BaseRepository):
    def getall(self, file_name = 'config/minertypes.conf'):
        raw = self.readrawfile(file_name)
        list = [domain.mining.MinerType(**k) for k in json.loads(raw)]
        return list
