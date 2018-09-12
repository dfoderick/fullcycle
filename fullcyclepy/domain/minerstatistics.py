
#"Pool Stale%": 0,
#"Discarded": 86497,
#"Diff": "65.5K",
#"Rejected": 15,
#"Proxy Type": "",
#"Getworks": 3311,
#"Last Share Time": "0:00:20",
#"Pool Rejected%": 0.1838,
#"Accepted": 8148,
#"Last Share Difficulty": 65536,
#"Difficulty Accepted": 533987328,
#"Has Stratum": true,
#"Priority": 1,
#"Stale": 3,
#"Long Poll": "N",
#"Quota": 1,
#"URL": "stratum+tcp://solo.antpool.com:3333",
#"Proxy": "",
#"Get Failures": 1,
#"Diff1 Shares": 0,
#"Best Share": 255598083,
#"Stratum Active": true,
#"POOL": 0,
#"Has GBT": false,
#"User": "antminer_1",
#"Status": "Alive",
#"Stratum URL": "solo.antpool.com",
#"Remote Failures": 1,
#"Difficulty Rejected": 983040,
#"Difficulty Stale": 0

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

