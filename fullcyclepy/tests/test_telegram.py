'''test telegram api'''
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

MESSAGE = 'Full Cycle Mining test {}'.format(APP.now())
APP.sendtelegrammessage(MESSAGE)

FILEOUT = APP.take_picture('fullcycle_camera.png')
APP.sendtelegramfile(FILEOUT)

APP.shutdown()
