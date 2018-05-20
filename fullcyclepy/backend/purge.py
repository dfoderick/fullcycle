'''purge all data. go back to clean slate'''
from backend.fcmapp import ApplicationService, CacheKeys

print('Starting application...')
APP = ApplicationService()
print('started', APP.component)

#purge cache
APP.cacheclear()
#purge rabbit
APP.shutdown()


