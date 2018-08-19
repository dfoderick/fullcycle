'''
test uploading a file to miner
'''

from domain.mining import Miner, MinerPool, AvailablePool, MinerCurrentPool, MinerStatistics, MinerStatus
from backend.fcmapp import ApplicationService

APP = ApplicationService()
APP.download_firmware()

MINER = Miner('test','','Antminer S9','192.168.1.218')
MINERTYPE = APP.get_miner_type(MINER.miner_type)

APP.antminer.load_firmware(MINER)
APP.antminer.set_frequency(MINER, '700')