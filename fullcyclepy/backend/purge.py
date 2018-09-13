'''purge all data. go back to clean slate'''
from backend.fcmapp import ApplicationService

print('Starting application...')
APP = ApplicationService()
print('started', APP.component)

#purge cache
APP.cache.purge()
#purge rabbit
APP.shutdown()
