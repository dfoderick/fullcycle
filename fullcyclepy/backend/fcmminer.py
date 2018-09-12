from helpers.antminerhelper import setminertoprivileged, privileged, setprivileged, setrestricted, waitforonline, restartmining, stopmining, restart, set_frequency

class Antminer():
    def __init__(self, config, login):
        self.__configuration = config
        self.__login = login

    def set_privileged(self, miner):
        setprivileged(miner, self.__login, self.__configuration.get('provision.apiallow.privileged'))

    def setminertoprivileged(self, miner):
        return setminertoprivileged(miner, self.__login, self.__configuration.get('provision.apiallow.privileged'))

    def set_restricted(self, miner):
        setrestricted(miner, self.__login, self.__configuration.get('provision.apiallow.restricted'))

    def waitforonline(self, miner):
        return waitforonline(miner)

    def getaccesslevel(self, miner):
        return privileged(miner)

    def restart(self, miner):
        return restart(miner)

    def stopmining(self, miner):
        '''stop miner through ssh.'''
        return stopmining(miner, self.__login)

    def restartssh(self, miner):
        '''restart miner through ssh. start mining again'''
        return restartmining(miner, self.__login)

    def set_frequency(self, miner, frequency):
        return set_frequency(miner, self.__login, frequency)
