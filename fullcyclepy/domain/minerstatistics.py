
class MinerStatistics(object):
    '''Statistics for a miner
    temperature and hash
    '''
    def __init__(self, miner, when=None, minercount=0, currenthash=0,
                 controllertemp=0,
                 tempboard1=0, tempboard2=0, tempboard3=0,
                 elapsed=0,
                 fan1='', fan2='', fan3='',
                 boardstatus1='', boardstatus2='', boardstatus3='',
                 frequency='', rawstats=None):
        self.miner = miner
        self.when = when
        self.minercount = minercount
        self.currenthash = currenthash
        self.controllertemp = controllertemp
        self.tempboard1 = tempboard1
        self.tempboard2 = tempboard2
        self.tempboard3 = tempboard3
        self.elapsed = elapsed
        self.fan1 = fan1
        self.fan2 = fan2
        self.fan3 = fan3
        self.boardstatus1 = boardstatus1
        self.boardstatus2 = boardstatus2
        self.boardstatus3 = boardstatus3
        self.frequency = frequency
        self.rawstats = rawstats

    def tempboardmax(self):
        return max(self.tempboard1, self.tempboard2, self.tempboard3)

    def format_elapsed(self):
        seconds = self.elapsed
        numdays = seconds // 86400
        numhours = (seconds % 86400) // 3600
        numminutes = ((seconds % 86400) % 3600) // 60
        numseconds = ((seconds % 86400) % 3600) % 60
        return '{0}:{1}:{2}:{3}'.format(numdays, numhours, numminutes, numseconds)

    def stats_summary(self):
        return '{0} {1}/{2} {3}'.format(self.currenthash, self.controllertemp, self.tempboardmax(), self.format_elapsed())

