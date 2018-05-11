'''#Full Cycle Mining Domain'''
from datetime import datetime, timezone

class MinerStatus:
    '''Status of Miner'''
    Online = 'online'
    Offline = 'offline'
    Disabled = 'disabled'

class MinerAccessLevel:
    Restricted = 'restricted'
    Privileged = 'priviledged'
    #not really a level, waiting for access upgrade
    Waiting = 'waiting'

class Login(object):
    """Login"""
    username = ''
    password = ''
    def __init__(self, username, password):
        self.username = username
        self.password = password

class MinerInfo(object):
    '''Meta information about a miner
    type and algo
    '''
    def __init__(self, miner_type, minerid):
        self.miner_type = miner_type
        self.minerid = minerid

class MinerCommand(object):
    """Command that could be sent to a miner"""
    def __init__(self, command='', parameter=''):
        self.command = command
        self.parameter = parameter

class Miner(object):
    """Miner"""
    #friendly name for your miner. keep it unique and non obscene for demos!
    name = ''
    #saved or derived from monitoring? status of the miner. online, offline,disabled etc
    laststatuschanged = None
    #saved or derived from monitoring? type of miner. Antminer S9, Antminer D3, etc.
    miner_type = ''
    #ip address, usuall will be local ip address. example: 192.168.x.y
    ipaddress = ''
    #ip port, usually will be 4028
    port = ''
    #the following are for mydevices. should move off of entity?
    username = ''
    password = ''
    #the mydevices clientid for device
    clientid = ''
    #network identifier for miner. usually the macaddress
    networkid = ''
    #so far have only seen Antminer S9 have the minerid from STATS command
    minerid = ''
    #last time the miner was monitored
    lastmonitor = None
    monitorcount = 0
    monitortime = 0
    #number of times miner is offline during this session
    offlinecount = 0
    #store is where the object was stored. mem is for memcache. should be moved out of domain
    store = ''
    #name of the pool that the miner should default to when it is provisioned
    defaultpool = ''
    #meta info on the miner. should be assigned during discovery and monitor
    minerinfo = None
    #TODO:MinerCurrentPool
    minerpool = None
    #TODO:MinerStatistics
    minerstats = None

    def __init__(self, name, status='', miner_type='', ipaddress='', port='', ftpport='', username='', password='', clientid='', networkid='', minerid='',
                 lastmonitor=None, offlinecount=0, defaultpool='', minerinfo=None, minerpool=None, minerstats=None, laststatuschanged = None):
        self.name = name
        self._status = status
        self.miner_type = miner_type
        self.ipaddress = ipaddress
        self.port = port
        self.ftpport = ftpport
        self.username = username
        self.password = password
        self.clientid = clientid
        self.networkid = networkid
        self.minerid = minerid
        self.lastmonitor = lastmonitor
        self.offlinecount = offlinecount
        self.defaultpool = defaultpool
        self.minerinfo = minerinfo
        self.minerpool = minerpool
        self.minerstats = minerstats
        self.laststatuschanged = laststatuschanged

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value != MinerStatus.Online and value != MinerStatus.Offline and value != MinerStatus.Disabled:
            raise ValueError('Invalid miner status {0}'.format(value))
        if self._status != value:
            self.laststatuschanged = datetime.utcnow()
        self._status = value

    def key(self):
        '''cache key for this entity'''
        if self.minerid is not None and self.minerid and self.minerid != 'unknown': return self.minerid
        if self.networkid is not None and self.networkid and str(self.networkid) != '{}': return str(self.networkid)
        if self.ipaddress is not None and self.ipaddress: return '{0}:{1}'.format(self.ipaddress, self.port)
        return self.name

    def set_ftp_port(self, port):
        if self.ftpport is not None and self.ftpport: return
        self.ftpport = port

    #todo: move ui code out of entity
    def summary(self):
        #datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%f%z')
        return '{0} {1} {2} {3}'.format(self.name, self.hash_or_offline(), self.formattime(self.lastmonitor), self.currentpoolname())

    def currentpoolname(self):
        if self.minerpool is None: return '?'
        #todo:look up pools here?
        return self.minerpool.poolname

    def hash_or_offline(self):
        '''hash or offline status of miner'''
        if self.status != MinerStatus.Online: return self.status
        if self.minerstats is None: return self.status
        return self.minerstats.stats_summary()

    #todo: move to appservice
    def utc_to_local(self, utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def formattime(self, time):
        '''format time'''
        if time is None: return ''
        if isinstance(time, datetime):
            return self.utc_to_local(time).strftime('%m-%d %H:%M:%S')
        stime = time
        if '.' in stime:
            stime = stime[0:stime.index('.') - 1]
        try:
            parsedtime = datetime.strptime(stime, '%Y-%m-%dT%H:%M:%S')
            return self.utc_to_local(parsedtime).strftime('%m-%d %H:%M:%S')
        except ValueError:
            return stime

    def uptime(self, seconds):
        minutes, _ = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return "%dd%dh%02dm" % (days, hours, minutes)

    #def updatefrom(self, otherminer):
    #    self.status = otherminer.status
    #    self.miner_type = otherminer.miner_type
    #    self.lastmonitor = otherminer.lastmonitor

    def is_disabled(self):
        if self.is_manually_disabled() or self.status == MinerStatus.Disabled:
            return True
        return False

    def is_manually_disabled(self):
        if self.name.startswith("#"):
            return True
        return False

    def can_monitor(self):
        if not self.ipaddress:
            return False
        if not self.port:
            return False
        return True

    def should_monitor(self):
        #always monitor at least once when fcm app starts up
        if self.lastmonitor is None:
            return True
        #no need to monitor if manually disabled
        if self.is_manually_disabled():
            return False
        if self.is_disabled():
            #keep monitoring if it was us that disabled the miner
            #need to keep monitoring (at longer interval) so we can detect when comes online
            #if its a planned outage then user should manually disable to stop monitoring
            #since = (datetime.utcnow() - self.lastmonitor).total_seconds()
            #if since > 10 * 60:
            return True
            #return False
        return True

    def offline_now(self):
        self.status = MinerStatus.Offline
        self.offlinecount += 1

    def online_now(self):
        self.status = MinerStatus.Online
        self.offlinecount = 0

    def is_send_offline_alert(self):
        #todo: make configurable
        if self.offlinecount <= 3:
            return True
        return False

    def monitored(self, stats, pool=None, info=None, sec=None):
        self.lastmonitor = datetime.utcnow()
        self.status = MinerStatus.Online
        if sec is not None:
            self.monitorcount += 1
            self.monitortime += sec
        #todo: process stats and pool
        self.setminerinfo(info)
        if pool is not None:
            self.minerpool = pool
        self.minerstats = stats

    def monitorresponsetime(self):
        if self.monitorcount == 0: return 0
        return self.monitortime/self.monitorcount

    def setminerinfo(self, info):
        if info is not None:
            self.minerinfo = info
            if not self.miner_type:
                self.miner_type = info.type
            if not self.minerid:
                self.minerid = info.minerid

    def updatefrom(self, updatedminer):
        if self.name != updatedminer.name:
            return
        self.setminerinfo(updatedminer.minerinfo)
        self.lastmonitor = updatedminer.lastmonitor
        self.status = updatedminer.status
        self.ipaddress = updatedminer.ipaddress
        self.port = updatedminer.port
        self.username = updatedminer.username
        self.password = updatedminer.password
        self.clientid = updatedminer.clientid
        self.networkid = updatedminer.networkid
        self.minerid = updatedminer.minerid
        self.offlinecount = updatedminer.offlinecount
        self.defaultpool = updatedminer.defaultpool
        if updatedminer.minerpool is not None:
            self.minerpool = updatedminer.minerpool

class Pool(object):
    """A configured Pool.
    Does not have to be attached to miner yet
    """
    pool_type = ''
    name = ''
    url = ''
    user = ''
    priority = ''
    password = 'x'

    def __init__(self, pool_type, name, url, user, priority):
        self.pool_type = pool_type
        self.name = name
        self.url = url
        self.user = user
        self.priority = priority

class MinerCurrentPool(object):
    '''The current pool where a miner is mining'''
    def __init__(self, miner, currentpool=None, currentworker=None, allpools=None):
        self.miner = miner
        self.poolname = '?'
        self.currentpool = currentpool
        self.currentworker = currentworker
        #allpools is a json object
        self.allpools = allpools

    def findpoolnumberforpool(self, url, worker):
        jpools = self.allpools["POOLS"]
        for pool in jpools:
            thisurl = pool["URL"]
            thisworker = pool["User"]
            if thisurl == url and thisworker.startswith(worker):
                return pool["POOL"]
        return None

class MinerPool(object):
    '''A pool that is available for a miner
    has a priority that can be switched.
    Links Miner to Pool
    '''
    def __init__(self, miner, priority, pool):
        self.miner = miner
        self.priority = priority
        self.pool = pool

class MinerStatistics(object):
    '''Statistics for a miner
    temperature and hash
    '''
    boardstatus1 = None
    boardstatus2 = None
    boardstatus3 = None
    def __init__(self, miner, when=None, minercount=0, currenthash=0,
                 controllertemp=0,
                 tempboard1=0, tempboard2=0, tempboard3=0,
                 elapsed=0,
                 fan1='', fan2='', fan3=''):
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

    def tempboardmax(self):
        return max(self.tempboard1, self.tempboard2, self.tempboard3)

    def stats_summary(self):
        return '{0} {1}/{2} {3}s'.format(self.currenthash, self.controllertemp, self.tempboardmax(), self.elapsed)
