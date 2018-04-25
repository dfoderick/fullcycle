'''send command to miner'''

from backend.fcmapp import ApplicationService, ComponentName
from helpers.antminerhelper import getminerconfig, print_response

APP = ApplicationService(ComponentName.fullcycle)

MINER = APP.getminerbyname('TEST')
MINER.ftpport = '22'

response = getminerconfig(MINER, APP.sshlogin())
print_response(response)

ACCESS_ORIGINAL = APP.antminer.getaccesslevel(MINER)
print('original', ACCESS_ORIGINAL)
if ACCESS_ORIGINAL != 'restricted':
    APP.antminer.set_restricted(MINER)
    APP.antminer.waitforonline(MINER)

ACCESS_RESTRICTED = APP.antminer.getaccesslevel(MINER)
print('restricted', ACCESS_RESTRICTED)
APP.antminer.set_privileged(MINER)
APP.antminer.waitforonline(MINER)

ACCESS_PRIVILEGED = APP.antminer.getaccesslevel(MINER)
print('privileged', ACCESS_PRIVILEGED)
#APP.antminer.restartssh(MINER)
#APP.antminer.waitforonline(MINER)

ACCESS_AFTERRESET = APP.antminer.getaccesslevel(MINER)
input('press any key...')