'''test telegram api'''
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

MESSAGE = 'Full Cycle Mining test {}'.format(APP.now())
if APP.configuration.is_enabled('telegram'):
    APP.telegram.sendmessage(MESSAGE)
else:
    print('telegram is not enabled in configuration')

if APP.configuration.is_enabled('camera'):
    FILEOUT = APP.camera.take_picture('fullcycle_camera.png')
    APP.telegram.sendphoto(FILEOUT)
else:
    print('camera is not enabled in configuration')


APP.shutdown()
