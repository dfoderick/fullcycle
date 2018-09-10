'''#raises event that will run the command
# a command listener must be running to listen for the command!
# publish to durable queue?
# TODO: allow pass in minername

#Examples:
#   runcommand.py switch S9102 3
'''
import sys
from helpers.queuehelper import QueueName
#from messaging.messages import *
from domain.mining import Miner, MinerCommand
from domain.rep import MinerRepository
from fcmapp import ApplicationService

APP = ApplicationService()

def findminerbyname(minertofind):
    miners = MinerRepository()
    miner = miners.getminerbyname(minertofind, APP.getconfigfilename('config/miners.conf'))
    if miner is None:
        miner = APP.getknownminerbyname(minertofind)
    if miner is None:
        miner = APP.getminer(Miner(name=minertofind))
    if miner is None:
        print('Miner {0} does not exist'.format(minertofind))
        sys.exit(1)
    return miner

def doit(args):
    if len(args) < 2:
        print('usage: python runcommand.py nameofcommand [nameofminer] [commandparameter]')
        APP.shutdown(1)

    cmd = args[1]
    if len(args) == 2:
        #single command, no miner specified
        if cmd == 'alert':
            APP.trybroadcast(cmd, '{0}: runcommand called on {1}'.format(APP.now(), cmd))
        else:
            APP.trypublish(cmd, '{0}: runcommand called on {1}'.format(APP.now(), cmd))
        print('sent command {0}'.format(cmd))
    else:
        minertofind = args[2]
        miner = findminerbyname(minertofind)
        cmdparam = ''
        if len(args) > 3:
            cmdparam = args[3]
        if not QueueName.has_value(cmd):
            print('Queue {0} is not valid'.format(cmd))
            sys.exit(1)

        if cmd:
            qmess = MinerCommand(cmd, cmdparam)
            msg = APP.createmessagecommand(miner, qmess)
            APP.bus.publish(queue_name=cmd, msg=msg)
            print('sent command {0} for miner {1}'.format(cmd, miner.name))

def main():
    if len(sys.argv) < 2:
        doit([sys.argv[0], 'provision', '192.168.1.117'])
    else:
        args = sys.argv[0:len(sys.argv)]
        doit(args)
    APP.shutdown()

if __name__ == "__main__":
    main()
