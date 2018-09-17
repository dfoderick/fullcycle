'''#Full Cycle Mining Domain'''
import time
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
    """Login name and password for access to miners"""
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

    def __init__(self, name, status=MinerStatus.Online, miner_type='', ipaddress='',
                 port='', ftpport='', username='', password='', clientid='', networkid='',
                 minerid='', lastmonitor=None, offlinecount=0, defaultpool='', minerinfo=None,
                 minerpool=None, minerstats=None, laststatuschanged=None,
                 in_service_date=None, location=None):
        #friendly name for your miner
        self.name = name
        self._status = status
        #saved or derived from monitoring? type of miner. Antminer S9, Antminer D3, etc.
        self.miner_type = miner_type
        #ip address, usuall will be local ip address. example: 192.168.x.y
        self.ipaddress = ipaddress
        #ip port, usually will be 4028
        self.port = port
        self.ftpport = ftpport
        self.username = username
        self.password = password
        #the mydevices clientid for device
        self.clientid = clientid
        #network identifier for miner. usually the macaddress
        self.networkid = networkid
        #so far have only seen Antminer S9 have the minerid from STATS command
        self.minerid = minerid
        #last time the miner was monitored
        self.lastmonitor = lastmonitor
        self.monitorcount = 0
        self.monitortime = 0
        #number of times miner is offline during this session
        self.offlinecount = offlinecount
        #name of the pool that the miner should default to when it is provisioned
        self.defaultpool = defaultpool
        #meta info on the miner. should be assigned during discovery and monitor
        self.minerinfo = minerinfo
        #MinerCurrentPool
        self.minerpool = minerpool
        #MinerStatistics
        self.minerstats = minerstats
        #status of the miner. online, offline,disabled etc
        self.laststatuschanged = laststatuschanged
        #store is where the object was stored. mem is for memcache.
        self.store = ''
        # the date that the miner was put into service or first discovered
        self.in_service_date = in_service_date
        # location of miner. could be name of facility or rack
        self.location = location
        #save a copy of the original key so we can detect if it changed
        self.key_original = self.key()

    @classmethod
    def create(cls, values):
        '''create entity from values dict'''
        miner = Miner('', '', '', '', '', '', '')
        #todo: find pythonic way to do this
        for pair in values:
            if 'minerid' in pair:
                miner.minerid = pair['minerid']
            if 'name' in pair:
                miner.name = pair['name']
            if 'ipaddress' in pair:
                miner.ipaddress = pair['ipaddress']
            if 'port' in pair:
                miner.port = pair['port']
            if 'location' in pair:
                miner.location = pair['location']
            if 'in_service_date' in pair:
                miner.in_service_date = Miner.to_date(pair['in_service_date'])
        return miner

    @classmethod
    def to_date(cls, dt):
        if dt is None:
            return dt
        if isinstance(dt, datetime):
            return dt
        #ISO8601 from javascript
        parsedtime = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')
        return Miner.utc_to_local(parsedtime)

    @property
    def is_key_updated(self):
        return self.key_original != self.key()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value != '' and value != MinerStatus.Online and value != MinerStatus.Offline and value != MinerStatus.Disabled:
            raise ValueError('Invalid miner status {0}'.format(value))
        if self._status != value:
            self.laststatuschanged = datetime.utcnow()
        self._status = value

    @property
    def pools_available(self):
        if self.minerpool is None:
            return None
        available = []
        if 'POOLS' in self.minerpool.allpools:
            jpools = self.minerpool.allpools['POOLS']
            for jpool in jpools:
                available.append(AvailablePool(pool_type=self.miner_type, named_pool=None, url=jpool['URL'], user=jpool['User'], priority=jpool['Priority']))
        return available

    #@property
    def key(self):
        '''cache key for this entity'''
        thekey = self.name
        if self.isvalid_minerid():
            thekey = self.minerid
        elif self.isvalid_networkid():
            thekey = str(self.networkid)
        elif self.isvalid_ipaddress():
            thekey = '{0}:{1}'.format(self.ipaddress, self.port)
        return thekey

    @property
    def is_unknown(self):
        return self.minerid == 'unknown'

    def isvalid_minerid(self):
        return self.minerid is not None and self.minerid and not self.is_unknown

    def isvalid_networkid(self):
        return self.networkid is not None and self.networkid and str(self.networkid) != '{}'

    def isvalid_ipaddress(self):
        return self.ipaddress is not None and self.ipaddress

    def set_ftp_port(self, port):
        if self.ftpport is not None and self.ftpport: return
        self.ftpport = port

    #todo: move ui code out of entity
    def summary(self):
        #datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%f%z')
        return '{0} {1} {2} {3}'.format(self.name, self.hash_or_offline(), self.formattime(self.lastmonitor), self.currentpoolname())

    def currentpoolname(self):
        if self.minerpool is None:
            return '?'
        #todo:look up pools here?
        return self.minerpool.poolname

    def hash_or_offline(self):
        '''hash or offline status of miner'''
        if self.status != MinerStatus.Online:
            return self.status
        if self.minerstats is None: return self.status
        return self.minerstats.stats_summary()

    @classmethod
    def utc_to_local(cls, utc_dt):
        '''#todo: move to appservice'''
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def formattime(self, ptime):
        '''format time'''
        if ptime is None:
            return ''
        if isinstance(ptime, datetime):
            return Miner.utc_to_local(ptime).strftime('%m-%d %H:%M:%S')
        stime = ptime
        if '.' in stime:
            stime = stime[0:stime.index('.') - 1]
        try:
            parsedtime = datetime.strptime(stime, '%Y-%m-%dT%H:%M:%S')
            return Miner.utc_to_local(parsedtime).strftime('%m-%d %H:%M:%S')
        except ValueError:
            return stime

    def uptime(self, seconds):
        minutes, _ = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return "%dd%dh%02dm" % (days, hours, minutes)

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
        if stats:
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
                self.miner_type = info.miner_type
            if not self.minerid:
                self.minerid = info.minerid

    def updatefrom(self, updatedminer):
        if self.minerid != updatedminer.minerid and self.name != updatedminer.name:
            return
        if self.minerid == updatedminer.minerid and self.name != updatedminer.name:
            self.name = updatedminer.name
        self.setminerinfo(updatedminer.minerinfo)

        #self.minerid = updatedminer.minerid
        fields = ['lastmonitor', 'status', 'ipaddress', 'port', 'username', 'password', 'clientid']
        fields.append('offlinecount')
        fields.append('defaultpool')
        fields.append('minerpool')
        fields.append('minerstats')
        fields.append('networkid')
        fields.append('location')
        fields.append('in_service_date')
        for fld in fields:
            val = getattr(updatedminer, fld)
            if val:
                setattr(self, fld, val)

class AvailablePool(object):
    """A pool available on a miner
    pool_type is the miner type (e.g. Antminer S9)
    """

    def __init__(self, pool_type, named_pool=None, url='', user='', password='x', priority=None):
        self.pool_type = pool_type
        self.named_pool = named_pool
        self.url = url
        self.user = user
        self.password = password
        self.priority = priority

    @property
    def key(self):
        return '{0}|{1}'.format(self.url, self.user)

class MinerApiCall(object):
    '''info about one call to miner'''
    def __init__(self, miner: Miner):
        self.miner = miner
        self.when = datetime.now()
        self.start_time = None
        self.stop_time = None

    def start(self):
        self.start_time = time.perf_counter()
    def stop(self):
        self.stop_time = time.perf_counter()
    def elapsed(self):
        return self.stop_time - self.start_time

class Pool(object):
    """A configured (Named) Pool.
    Does not have to be attached to miner yet
    """

    def __init__(self, pool_type, name, url, user, priority, password='x'):
        self.pool_type = pool_type
        self.name = name
        self.url = url
        self.user = user
        self.priority = priority
        self.password = password

    @classmethod
    def create(cls, values):
        '''create entity from values dict'''
        entity = Pool('', '', '', '', '')
        #todo: find pythonic way to do this
        for pair in values:
            if 'pool_type' in pair:
                entity.pool_type = pair['pool_type']
            if 'name' in pair:
                entity.name = pair['name']
            if 'url' in pair:
                entity.url = pair['url']
            if 'user' in pair:
                entity.user = pair['user']
            if 'priority' in pair:
                entity.priority = pair['priority']
            if 'password' in pair:
                entity.password = pair['password']
        return entity


    def is_same_as(self, available_pool: AvailablePool):
        return available_pool.url == self.url and available_pool.user.startswith(self.user)

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
