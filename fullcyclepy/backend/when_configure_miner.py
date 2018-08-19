'''when miner configuration needs to be changed
set frequency or fan setting
'''
from helpers.queuehelper import QueueName, QueueEntries
from domain import mining
from fcmapp import Component

CONFIGURE = Component('fullcycle')

def when_configure(channel, method, properties, body):
    print("[{0}] Received miner configure message".format(CONFIGURE.app.now()))
    try:
        minermsg = CONFIGURE.app.messagedecodeminercommand(body)

        entries = doconfigure(minermsg, minermsg.command)
        CONFIGURE.app.enqueue(entries)
    except Exception as ex:
        CONFIGURE.app.logexception(ex)

def doconfigure(miner: mining.Miner, command: mining.MinerCommand):
    if command.command == "frequency":
        CONFIGURE.app.antminer.set_frequency(miner, command.parameter)

    if command.command == "fan":
        #TODO:
        pass

def main():
    CONFIGURE.listeningqueue = CONFIGURE.app.subscribe(QueueName.Q_CONFIGURE, when_configure)
    CONFIGURE.listen()

if __name__ == "__main__":
    main()

