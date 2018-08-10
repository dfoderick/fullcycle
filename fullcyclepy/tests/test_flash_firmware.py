'''
test uploading a file to miner
'''

from domain.mining import Miner, MinerPool, AvailablePool, MinerCurrentPool, MinerStatistics, MinerStatus
from backend.fcmapp import ApplicationService

APP = ApplicationService()

MINER = Miner('test','','Antminer S9','192.168.1.218')

#APP.antminer.load_firmware(MINER)
APP.antminer.set_frequency(MINER, '700')