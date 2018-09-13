'''Full Cycle Mining Systems Check'''
import datetime
from colorama import Fore
import backend.fcmutils as utils
from backend.fcmapp import ApplicationService
from domain.loggingrepository import getminerlog
from domain.logging import MinerLog

print('Starting application...')
APP = ApplicationService()
print('started', APP.component)

APP.tryputcache(key='test', value='value')
CACHE_VALUE = utils.safestring(APP.cache.trygetvaluefromcache('test'))
if CACHE_VALUE == 'value':
    print(Fore.GREEN+'cache is working')
else:
    print(Fore.RED+'cache is broken')

try:
    SUCCESS = APP.alert('Full Cycle diagnostics test')
    if SUCCESS:
        print(Fore.GREEN+'message bus is working')
    else:
        print(Fore.RED+'message bus is broken')
except BaseException as ex:
    print(Fore.RED+'message bus is broken')
    print(APP.exceptionmessage(ex))

try:
    LOG = MinerLog()
    LOG.createdate = datetime.datetime.utcnow()
    LOG.minerid = 'diag'
    LOG.minername = 'diagnostics'
    LOG.action = 'diagnostics'
    SUCCESS = APP.log_mineractivity(LOG)

    LOGS = getminerlog(APP.getsession())
    #print(log.__dict__)
    LOG_CNT = 0
    for log in LOGS:
        LOG_CNT += 1

    if SUCCESS and LOG_CNT > 0:
        print(Fore.GREEN+'database is working, {0} logs'.format(LOG_CNT))
    else:
        print(Fore.RED+'database is broken')
except BaseException as ex:
    print(Fore.RED+'database is broken')
    print(APP.exceptionmessage(ex))
