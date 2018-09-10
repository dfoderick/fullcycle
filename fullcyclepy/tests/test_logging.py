'''test logging'''
from backend.fcmcomponent import ComponentName
from backend.fcmapp import ApplicationService

APP = ApplicationService(ComponentName.fullcycle)

APP.loginfo('Unit Test Info')
APP.logdebug('Unit Test Debug')
APP.logerror('Unit Test Error')
