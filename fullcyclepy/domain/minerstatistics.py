
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
                 frequency='', hardware_errors=0, hash_avg=0, rawstats=None):
        self.miner = miner
        self.when = when
        self.minercount = minercount
        self.currenthash = currenthash
        self.controllertemp = controllertemp
        self.tempboard1 = tempboard1
        self.tempboard2 = tempboard2
        self.tempboard3 = tempboard3
        #elapsed time in seconds
        self.elapsed = elapsed
        self.fan1 = fan1
        self.fan2 = fan2
        self.fan3 = fan3
        self.boardstatus1 = boardstatus1
        self.boardstatus2 = boardstatus2
        self.boardstatus3 = boardstatus3
        self.frequency = frequency
        self.hardware_errors = hardware_errors
        self.hash_avg = hash_avg
        self.rawstats = rawstats

    @property
    def hardware_errors_per_second(self):
        if self.elapsed == 0:
            return None
        return self.hardware_errors/self.elapsed

    @property
    def hardware_errors_per_minute(self):
        if self.elapsed == 0:
            return None
        seconds_per_minute = 60
        if self.elapsed < seconds_per_minute:
            return None
        minutes = self.elapsed / seconds_per_minute
        return self.hardware_errors/minutes

    @property
    def hardware_errors_per_hour(self):
        if self.elapsed == 0:
            return None
        seconds_per_hour = 60 * 60
        if self.elapsed < seconds_per_hour:
            return None
        hours = self.elapsed / seconds_per_hour
        return self.hardware_errors/hours

    @property
    def hardware_errors_per_day(self):
        if self.elapsed == 0:
            return None
        seconds_per_day = 60 * 60 * 24
        if self.elapsed < seconds_per_day:
            return None
        day = self.elapsed / seconds_per_day
        return self.hardware_errors/day

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
