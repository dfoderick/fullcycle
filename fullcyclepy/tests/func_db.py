'''test connectivity with database'''
#currently using MariaDB (mysql)
#mysql  Ver 15.1 Distrib 10.1.23-MariaDB, for debian-linux-gnueabihf (armv7l) using readline 5.2

import datetime
from domain.logging import MinerLog
from domain.loggingrepository import getminerlog
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

LOG = MinerLog()
LOG.createdate = datetime.datetime.utcnow()
LOG.minerid = 'unit test'
LOG.minername = 'unit test'
LOG.action = 'unit test'
APP.log_mineractivity(LOG)

for log in getminerlog(APP.getsession()):
    print(log.__dict__)
