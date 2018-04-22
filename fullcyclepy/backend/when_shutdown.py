'''shut down a miner'''
from helpers.queuehelper import QueueName, Queue
from helpers.antminerhelper import shutdown
from fcmapp import Component

SHUTDOWN = Component('shutdown')

def when_shutdown(channel, method, properties, body):
    msg = SHUTDOWN.app.messagedecodeminer(body)
    miner = msg.miner
    minercommand = msg.command
    #sanity check
    if minercommand.command == 'shutdown':
        #here you implement specific logic to shutdown your miner
        shutdown(miner, SHUTDOWN.app.sshlogin())

def main():
    qshut = Queue(QueueName.Q_SHUTDOWN, SHUTDOWN.app.getservice('rabbit'))
    qshut.subscribe(when_shutdown)

    print('Waiting for shutdown command. To exit press CTRL+C')
    SHUTDOWN.app.listen(qshut)

if __name__ == "__main__":
    main()
