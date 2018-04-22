'''send command to miner'''

from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

MINER = APP.getminerbyname('TEST')
MINER.ftpport = '22'
ACCESS_ORIGINAL = APP.antminer.getaccesslevel(MINER)
if ACCESS_ORIGINAL != 'restricted':
    APP.antminer.set_restricted(MINER)
    APP.antminer.waitforonline(MINER)
ACCESS_RESTRICTED = APP.antminer.getaccesslevel(MINER)
APP.antminer.set_privileged(MINER)
APP.antminer.waitforonline(MINER)
ACCESS_PRIVILEGED = APP.antminer.getaccesslevel(MINER)
#APP.antminer.restartssh(MINER)
#APP.antminer.waitforonline(MINER)
ACCESS_AFTERRESET = APP.antminer.getaccesslevel(MINER)
