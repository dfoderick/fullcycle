'''test miner summary'''

from backend.fcmapp import ApplicationService

FCM = ApplicationService('test')

print(FCM.minersummary())

FCM.shutdown()
