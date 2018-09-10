'''monitor miners, bypassing the queues'''

#do not remove! needed
import json #pylint: disable=unused-import
#from helpers import antminerhelper
from backend.fcmapp import ApplicationService
from backend.doflow_handlemessages import dispatchmessages

from backend.when_monitor import domonitor

def main():
    '''main'''
    mainapp = ApplicationService(component='monitor', option='')
    entries = domonitor()
    dispatchmessages(mainapp, entries)
    print('done')

if __name__ == "__main__":
    main()
