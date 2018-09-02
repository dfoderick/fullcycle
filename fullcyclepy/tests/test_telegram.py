'''test telegram api'''
from backend.fcmapp import ApplicationService, ComponentName

APP = ApplicationService(ComponentName.fullcycle)

MESSAGE = 'Full Cycle Mining test {}'.format(APP.now())
if APP.is_enabled_configuration('telegram'):
    APP.sendtelegrammessage(MESSAGE)
else:
    print('telegram is not enabled in configuration')

if APP.is_enabled_configuration('camera'):
    FILEOUT = APP.take_picture('fullcycle_camera.png')
    APP.sendtelegramphoto(FILEOUT)
else:
    print('camera is not enabled in configuration')


APP.shutdown()
