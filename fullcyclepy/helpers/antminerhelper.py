'''# Miner Helper functions
# Skylake Software, Inc
#"bitmain-fan-ctrl" : true,
#"bitmain-fan-pwm" : "80",
'''
import time
import datetime
from helpers.minerapi import MinerApi
from helpers.ssh import Ssh
from domain.mining import Miner, MinerInfo, MinerStatistics, MinerCurrentPool, MinerAccessLevel

class MinerMonitorException(Exception):
    """Happens during monitoring of miner"""
    def friendlymessage(self):
        msg = getattr(self, 'message', repr(self))
        return msg

    def istimedout(self):
        return self.friendlymessage().find('timed out') >= 0
    def isconnectionrefused(self):
        return self.friendlymessage().find('ConnectionRefusedError') >= 0

class MinerCommandException(Exception):
    """Happens during executing miner command"""

def getminerinfo(miner: Miner):
    minerid = 'unknown'
    minertype = 'unknown'
    if not miner.can_monitor():
        raise MinerMonitorException('miner {0} cannot be monitored. ip={1} port={2}'.format(miner.name, miner.ipaddress, miner.port))
    api = MinerApi(host=miner.ipaddress, port=int(miner.port), timeout=1)
    jstats = api.stats()
    #if there was an error then the return is STATUS not STATS!
    toplevelstatus = jstats['STATUS'][0]
    if toplevelstatus['STATUS'] == 'error':
        if not miner.is_disabled():
            raise MinerMonitorException(toplevelstatus['description'])
    else:
        status = jstats['STATS'][0]
        details = jstats['STATS'][1]
        if 'Type' in status:
            minertype = status['Type']
        else:
            if toplevelstatus['Description'].startswith('cgminer'):
                minertype = toplevelstatus['Description']
        if minertype.startswith('Antminer S9'):
            minerid = details['miner_id']
    minerinfo = MinerInfo(minertype, minerid)
    return minerinfo

def stats(miner: Miner):
    try:
        entity = MinerStatistics(miner, when=datetime.datetime.utcnow())
        api = MinerApi(host=miner.ipaddress, port=int(miner.port))
        jstats = api.stats()
        if jstats['STATUS'][0]['STATUS'] == 'error':
            if not miner.is_disabled():
                raise MinerMonitorException(jstats['STATUS'][0]['description'])
        else:
            status = jstats['STATS'][0]
            jsonstats = jstats['STATS'][1]
            entity.minercount = int(jsonstats['miner_count'])
            entity.elapsed = int(jsonstats['Elapsed'])
            entity.currenthash = int(float(jsonstats['GHS 5s']))
            minertype = status['Type']
            entity.controllertemp = None
            if 'temp_max' in jsonstats:
                entity.controllertemp = jsonstats['temp_max']
            #should be 3
            #tempcount = jsonstats['temp_num']
            if minertype.startswith('Antminer S9'):
                entity.tempboard1 = int(jsonstats['temp2_6'])
                entity.tempboard2 = int(jsonstats['temp2_7'])
                entity.tempboard3 = int(jsonstats['temp2_8'])
                entity.boardstatus1 = jsonstats['chain_acs6']
                entity.boardstatus2 = jsonstats['chain_acs7']
                entity.boardstatus3 = jsonstats['chain_acs8']
                entity.fan1 = jsonstats['fan3']
                entity.fan2 = jsonstats['fan6']
            if minertype == 'Antminer D3':
                entity.tempboard1 = int(jsonstats['temp2_1'])
                entity.tempboard2 = int(jsonstats['temp2_2'])
                entity.tempboard3 = int(jsonstats['temp2_3'])
            if minertype == 'Antminer A3':
                entity.tempboard1 = int(jsonstats['temp2_1'])
                entity.tempboard2 = int(jsonstats['temp2_2'])
                entity.tempboard3 = int(jsonstats['temp2_3'])
            return entity
    except BaseException as ex:
        print('Failed to call miner stats api: ' + str(ex))
        raise MinerMonitorException(ex)
    return None

def pools(miner: Miner):
    '''Gets the current pool for the miner'''
    def sort_by_priority(j):
        return j['Priority']
    try:
        api = MinerApi(host=miner.ipaddress, port=int(miner.port))
        jstatuspools = api.pools()
        if jstatuspools['STATUS'][0]['STATUS'] == 'error':
            if not miner.is_disabled():
                raise MinerMonitorException(jstatuspools['STATUS'][0]['description'])
        else:
            jpools = jstatuspools["POOLS"]
            #sort by priority
            jpools.sort(key=sort_by_priority)
            #try to do elegant way, but not working
            #cPool = namedtuple('Pool', 'POOL, URL, Status,Priority,Quota,Getworks,Accepted,Rejected,Long Poll')
            #colpools = [cPool(**k) for k in jsonpools["POOLS"]]
            #for pool in colpools:
            #    print(pool.POOL)
            for pool in jpools:
                if str(pool["Status"]) == "Alive":
                    currentpool = pool["URL"]
                    currentworker = pool["User"]
                    #print("{0} {1} {2} {3} {4} {5}".format(pool["POOL"],pool["Priority"],pool["URL"],pool["User"],pool["Status"],pool["Stratum Active"]))
                    break
            minerpool = MinerCurrentPool(miner, currentpool, currentworker, jstatuspools)
            return minerpool
    except BaseException as ex:
        print('Failed to call miner pools api: ' + str(ex))
    return None

def getminerlcd(miner: Miner):
    '''gets a summary (quick display values) for the miner'''
    try:
        api = MinerApi(host=miner.ipaddress, port=int(miner.port))
        jstatuspools = api.lcd()
        return jstatuspools
    except BaseException as ex:
        return str(ex)

def setminertoprivileged(miner, login, allowsetting):
    try:
        mineraccess = privileged(miner)
    except MinerMonitorException as ex:
        if ex.istimedout():
            mineraccess = MinerAccessLevel.Waiting
    if mineraccess == MinerAccessLevel.Restricted or mineraccess == MinerAccessLevel.Waiting:
        if mineraccess == MinerAccessLevel.Restricted:
            setprivileged(miner, login, allowsetting)
        #todo: not ideal to wait in a loop here, need a pattern that will wait in non blocking mode
        waitforonline(miner)
        mineraccess = privileged(miner)
    return mineraccess

def privileged(miner: Miner):
    '''gets status: privileged or restricted'''
    api = MinerApi(host=miner.ipaddress, port=int(miner.port))
    apiresponse = api.privileged()
    jstatus = apiresponse["STATUS"][0]
    if jstatus is not None and jstatus["STATUS"] == "S":
        return MinerAccessLevel.Privileged
    return MinerAccessLevel.Restricted

#restart (*)   none           Status is a single "RESTART" reply before cgminer restarts
def restart(miner: Miner):
    '''restart miner through api'''
    api = MinerApi(host=miner.ipaddress, port=int(miner.port))
    apiresponse = api.restart()
    print(apiresponse)
    return apiresponse

def print_connection_data(connection):
    if connection.strdata:
        print(connection.strdata)    # print the last line of received data
        print('==========================')
    if connection.alldata:
        print(connection.alldata)   # This contains the complete data received.
        print('==========================')

def print_response(response):
    for line in response:
        print(line)

def getportfromminer(miner: Miner):
    if isinstance(miner.ftpport, int): return miner.ftpport
    if isinstance(miner.ftpport, str) and miner.ftpport:
        tryport = int(miner.ftpport)
        if tryport > 0: return tryport
    return 22

def getminerconfig(miner: Miner, login):
    '''ger the miner config file'''
    connection = Ssh(miner.ipaddress, login.username, login.password, port=getportfromminer(miner))
    config = connection.exec_command('cat /config/{0}.conf'.format(getminerfilename(miner)))
    connection.close_connection()
    return config

def restartminer(miner: Miner, login):
    '''restart miner through ssh'''
    connection = Ssh(miner.ipaddress, login.username, login.password, port=getportfromminer(miner))
    connection.open_shell()
    connection.send_shell('/etc/init.d/{0}.sh restart'.format(getminerfilename(miner)))
    time.sleep(15)
    print_connection_data(connection)
    connection.close_connection()

def changesshpassword(miner: Miner, oldlogin, newlogin):
    """ change the factory ssh password """
    if newlogin.username != oldlogin.username:
        print("changesshpassword: currently username change is not supported. only change password")
        return
    connection = Ssh(miner.ipaddress, oldlogin.username, oldlogin.password, port=getportfromminer(miner))
    connection.open_shell()
    connection.send_shell('echo "{0}:{1}" | chpasswd'.format(newlogin.username, newlogin.password))
    time.sleep(5)
    print_connection_data(connection)
    connection.close_connection()

def reboot(miner: Miner, login):
    """ reboot the miner through ftp """
    connection = Ssh(miner.ipaddress, login.username, login.password, port=getportfromminer(miner))
    connection.open_shell()
    response = connection.exec_command('/sbin/reboot')
    print_connection_data(connection)
    connection.close_connection()
    return response

def shutdown(miner: Miner, login):
    """ shutdown the miner through ftp
    Warning! this will not turn off the power to the machine!
    It will only shut down the operating system. Machine will still be consuming power if power supply
    does not have on/off switch. You will have to manually restart the machine.
    """
    connection = Ssh(miner.ipaddress, login.username, login.password, port=getportfromminer(miner))
    connection.open_shell()
    connection.send_shell('/sbin/poweroff')
    time.sleep(5)
    print_connection_data(connection)
    connection.close_connection()

def waitforonline(miner: Miner):
    #poll miner until it comes up, returns MinerInfo or None for timeout
    cnt = 60
    sleeptime = 5
    minerinfo = None
    while cnt > 0:
        try:
            minerinfo = getminerinfo(miner)
            return minerinfo
        except MinerMonitorException as ex:
            if not ex.istimedout() and not ex.isconnectionrefused():
                raise ex
            else:
                print(ex.friendlymessage())

        if minerinfo is not None:
            if minerinfo.miner_type:
                print('   found {0} {1}'.format(minerinfo.miner_type, minerinfo.minerid))
                cnt = 0
        if cnt > 0:
            cnt -= sleeptime
            print('Waiting for {0}...'.format(miner.name))
            time.sleep(sleeptime)
    return None


#The 'poolpriority' command can be used to reset the priority order of multiple
#pools with a single command - 'switchpool' only sets a single pool to first priority
#Each pool should be listed by id number in order of preference (first = most preferred)
#Any pools not listed will be prioritised after the ones that are listed, in the
#priority order they were originally
#If the priority change affects the miner's preference for mining, it may switch immediately
def switch(miner: Miner, poolnumber):
    api = MinerApi(host=miner.ipaddress, port=int(miner.port))
    jswitch = api.switchpool("{0}".format(poolnumber))
    print(jswitch["STATUS"][0]["Msg"])

 #addpool|URL,USR,PASS (*)
 #              none           There is no reply section just the STATUS section
 #                             stating the results of attempting to add pool N
 #                             The Msg includes the pool number and URL
 #                             Use '\\' to get a '\' and '\,' to include a comma
 #                             inside URL, USR or PASS
def addpool(miner: Miner, pool):
    """ Add a pool to a miner. Allows user to select it from drop down and easily switch to it """
    api = MinerApi(host=miner.ipaddress, port=int(miner.port))
    jaddpool = api.addpool("{0},{1},{2}".format(pool.url, pool.user, "x"))
    return jaddpool["STATUS"][0]["Msg"]

def getminerfilename(miner: Miner):
    '''cgminer for D3 and A3'''
    minerfilename = 'cgminer'
    if miner.miner_type.startswith('Antminer S9'):
        minerfilename = 'bmminer'
    return minerfilename

def change_setting(settingkey, newvalue):
    '''todo:there is bug here if updating the last line of config file! command (,) not needed at end'''
    return "sed -i \'s_^\\(\"{0}\" : \\).*_\\1\"{1}\",_\'".format(settingkey, newvalue)

def get_changeconfigcommands(configfilename, setting, newvalue):
    commands = []
    commands.append('cd /config')
    commands.append('cp {0}.conf {1}_last.conf'.format(configfilename, configfilename))
    commands.append('chmod u=rw {0}.conf'.format(configfilename))
    commands.append("{0} {1}.conf".format(change_setting(setting, newvalue), configfilename))
    commands.append('chmod u=r {0}.conf'.format(configfilename))
    return commands

def sendcommands_and_restart(miner: Miner, login, commands):
    connection = Ssh(miner.ipaddress, login.username, login.password, port=getportfromminer(miner))
    connection.open_shell()
    for cmd in commands:
        connection.send_shell(cmd)
    time.sleep(5)
    print_connection_data(connection)
    connection.close_connection()
    restartminer(miner, login)

def setprivileged(miner: Miner, login, allowsetting):
    """ Set miner to privileged mode """
    commands = get_changeconfigcommands(getminerfilename(miner), 'api-allow', allowsetting)
    sendcommands_and_restart(miner, login, commands)

def setrestricted(miner: Miner, login, allowsetting):
    """ Set miner to restricted mode """
    commands = get_changeconfigcommands(getminerfilename(miner), 'api-allow', allowsetting)
    sendcommands_and_restart(miner, login, commands)

def set_frequency(miner: Miner, login, frequency):
    """ Set miner frequency
    Does not work for S9 with auto tune"""
    #default for S9 is 550
    #"bitmain-freq" : "550",
    commands = get_changeconfigcommands(getminerfilename(miner), 'bitmain-freq', frequency)
    sendcommands_and_restart(miner, login, commands)
