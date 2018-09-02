'''Test saving application data'''
'''
    Requires services to be running.
    Redis
'''

from domain.mining import Miner
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

KNOWN = APP.allminers()
CNT = len(KNOWN)

MINER = Miner('New Miner2','','','192.168.1.2','4028','','')
APP.save_miner(MINER)

KNOWN2 = APP.allminers()

CNT2 = len(KNOWN2)
print(CNT2)

APP.save_miner(MINER)

KNOWN3 = APP.allminers()

CNT3 = len(KNOWN3)
print(CNT3)

