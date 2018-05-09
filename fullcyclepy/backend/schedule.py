'''#runs tasks on schedule
#should read tasks from configuration
#examples: when to discover. when to monitor. when to ...
#will run tasks by sending command (raising event)
'''
import datetime
import time
from helpers.queuehelper import QueueName, QueueEntry
from helpers.taskschedule import TaskSchedule
from domain.sensors import SensorValue
from fcmapp import ApplicationService

#one-time schedule provision when app starts up
APP = ApplicationService(component='schedule')
APP.send(QueueName.Q_POOLCONFIGURATIONCHANGED, '')
SLEEP_SECONDS = APP.configuration('schedule.sleep.seconds')

HEARTBEAT = TaskSchedule(run_on_init=True)
HEARTBEAT.start = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
HEARTBEAT.interval = 60 * APP.configuration('schedule.hearbeat.minutes')

MONITOR = TaskSchedule(run_on_init=True)
MONITOR.interval = APP.configuration('schedule.monitor.seconds')

DISCOVER = TaskSchedule(run_on_init=True)
DISCOVER.interval = 60 * APP.configuration('schedule.discover.minutes')

CAMERA = TaskSchedule(run_on_init=True)
CAMERA.start = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
CAMERA.interval = 60 * APP.configuration('schedule.camera.minutes')

TEMPERATURE = TaskSchedule(run_on_init=True)
TEMPERATURE.start = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
TEMPERATURE.interval = 60 * APP.configuration('schedule.temperature.minutes')

UPDATEWEB = TaskSchedule(run_on_init=False)
UPDATEWEB.interval = 60 * APP.configuration('update.fullcycleweb.interval.minutes')

while True:
    try:
        if MONITOR.is_time_to_run():
            print("[{0}] Time to monitor".format(APP.now()))
            print('Pushing monitor command to {0}.'.format(QueueName.Q_MONITOR))
            APP.send(QueueName.Q_MONITOR, 'monitor')
            MONITOR.lastrun = datetime.datetime.now()

        if DISCOVER.is_time_to_run():
            print("[{0}] Time to discover".format(APP.now()))
            print('Pushing discover command to {0}.'.format(QueueName.Q_DISCOVER))
            APP.send(QueueName.Q_DISCOVER, 'discover')
            DISCOVER.lastrun = datetime.datetime.now()

        if CAMERA.is_time_to_run():
            if APP.is_enabled_configuration('telegram') and APP.is_enabled_configuration('camera'):
                print("[{0}] sending camera".format(APP.now()))
                photo_name = APP.take_picture()
                APP.store_picture_cache(photo_name)
                APP.sendtelegramphoto(photo_name)
            CAMERA.lastrun = datetime.datetime.now()

        if TEMPERATURE.is_time_to_run():
            if APP.is_enabled_configuration('temperature') and APP.is_enabled_configuration('telegram'):
                print("[{0}] sending temperature".format(APP.now()))
                SENSOR_HUMID, SENSOR_TEMP = APP.readtemperature()
                if SENSOR_HUMID is not None or SENSOR_TEMP is not None:
                    MESSAGE = '{0}: Temp={1:0.1f}*  Humidity={2:0.1f}%'.format(APP.now(), SENSOR_TEMP, SENSOR_HUMID)
                    APP.sendtelegrammessage(MESSAGE)
            TEMPERATURE.lastrun = datetime.datetime.now()

        if HEARTBEAT.is_time_to_run():
            print("[{0}] sending heartbeat".format(APP.now()))
            MSG = 'At {0}'.format(APP.now())
            #get summary of known miners. name, hash or offline, pool
            if APP.is_enabled_configuration('temperature'):
                SENSOR_HUMID, SENSOR_TEMP = APP.readtemperature()
                if SENSOR_HUMID is not None and SENSOR_TEMP is not None:
                    MSG = MSG + 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(SENSOR_TEMP, SENSOR_HUMID)
            MSG = MSG + '\n{0}'.format(APP.minersummary())
            if APP.is_enabled_configuration('telegram'):
                APP.sendtelegrammessage(MSG)
            APP.sendqueueitem(QueueEntry(QueueName.Q_LOG, MSG, 'broadcast'))
            HEARTBEAT.lastrun = datetime.datetime.now()

        if UPDATEWEB.is_time_to_run():
            print("[{0}] check for web update".format(APP.now()))
            print('Pushing update web  command to {0}.'.format(QueueName.Q_UPDATEWEB))
            APP.send(QueueName.Q_UPDATEWEB, 'updateweb')
            UPDATEWEB.lastrun = datetime.datetime.now()


        time.sleep(SLEEP_SECONDS)

    except KeyboardInterrupt:
        APP.shutdown()
    except BaseException as ex:
        print('App Error: ' + APP.exceptionmessage(ex))
