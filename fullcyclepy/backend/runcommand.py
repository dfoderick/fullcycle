'''#raises event that will run the command
# a command listener must be running to listen for the command!
# publish to durable queue?
# TODO: allow pass in minername

#Examples:
#   runcommand.py switch S9102 3
'''
import sys
from helpers.queuehelper import QueueName, Queue, BroadcastSender
#from messaging.messages import *
from domain.mining import Miner, MinerCommand
from domain.rep import MinerRepository
from fcmapp import ApplicationService

APP = ApplicationService()

def doit(args):
    if len(args) < 2:
        print('usage: python runcommand.py nameofcommand [nameofminer] [commandparameter]')
        APP.shutdown(1)

    cmd = args[1]
    if len(args) == 2:
        #single command, no miner specified
        if cmd == 'alert':
            queue_command = BroadcastSender(cmd, APP.getservice('rabbit'))
            APP.trybroadcast(queue_command, '{0}: runcommand called on {1}'.format(APP.now(), cmd))
            queue_command.close()
        else:
            queue_command = Queue(cmd, APP.getservice('rabbit'))
            queue_command.publish('{0}: runcommand called on {1}'.format(APP.now(), cmd))
            queue_command.close()
        print('sent command {0}'.format(cmd))
    else:
        minertofind = args[2]
        cmdparam = ''
        if len(args) > 3:
            cmdparam = args[3]
        miners = MinerRepository()
        miner = miners.getminerbyname(minertofind, APP.getconfigfilename('config/miners.conf'))
        if miner is None:
            miner = APP.getknownminerbyname(minertofind)
        if miner is None:
            miner = APP.getminer(Miner(name=minertofind))
        if miner is None:
            print('Miner {0} does not exist'.format(minertofind))
            sys.exit(1)
        qnames = QueueName()
        if not qnames.isvalidqname(cmd):
            print('Queue {0} is not valid'.format(cmd))
            sys.exit(1)
        queue_command = Queue(cmd, APP.getservice('rabbit'))
        #TODO: cleanup logic here. when to call app and when to override with just miner and command
        if cmd:
            qmess = MinerCommand(cmd, cmdparam)
            msg = APP.createmessagecommand(miner, qmess)
            queue_command.publish(msg)
        else:
            queue_command.publish(APP.messageencode(miner))
        queue_command.close()
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
