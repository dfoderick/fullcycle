'''Full Cycle Mining Systems Check'''
import datetime
from colorama import Fore
from backend.fcmapp import ApplicationService
from domain.loggingrepository import getminerlog
from domain.logging import MinerLog

print('Starting application...')
APP = ApplicationService()
print('started',APP.component)

APP.tryputcache(key='test',value='value')
CACHE_VALUE = APP.safestring(APP.trygetvaluefromcache('test'))
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
    log = MinerLog()
    log.createdate = datetime.datetime.utcnow()
    log.minerid = 'diag'
    log.minername = 'diagnostics'
    log.action = 'diagnostics'
    SUCCESS = APP.log_mineractivity(log)

    for log in getminerlog(APP.getsession()):
        print(log.__dict__)

    if SUCCESS:
        print(Fore.GREEN+'database is working')
    else:
        print(Fore.RED+'database is broken')
except BaseException as ex:
        print(Fore.RED+'database is broken')
        print(APP.exceptionmessage(ex))
