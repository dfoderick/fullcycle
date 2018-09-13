'''
# listens for statistics updated and run rules on them
# some rules can run just from the last statistics
# other rules will need to be enforced from the history of the miner
'''
import datetime
import json
from colorama import Fore
from helpers.queuehelper import QueueName, QueueEntries
from domain.mining import MinerCommand
from domain.miningrules import MinerStatisticsRule
from domain.logging import MinerLog
from backend.fcmcomponent import ComponentName
from backend.fcmapp import Component

class ComponentRunRules(Component):
    '''component for running rules'''
    def __init__(self):
        self.alertstext = ''
        super().__init__(componentname=ComponentName.rules, option='')

    def addalert(self, alertmsg):
        self.alertstext += alertmsg
        return alertmsg

RULES = ComponentRunRules()

def rules(miner, minerstats, minerpool):
    '''this runs the rules'''
    entries = QueueEntries()
    if miner is None or minerstats is None:
        return entries
    savedminer = RULES.app.getminer(miner)
    broken = gather_broken_rules(savedminer, minerstats)
    if broken:
        #TODO: could raise broken rule event???
        for rule in broken:
            RULES.app.log_mineractivity(make_log_from_rule(rule))
            add_entry_for_rule(entries, rule)
    return entries

def gather_broken_rules(savedminer, minerstats):
    broken = []
    for ruleparms in RULES.app.ruleparameters():
        rule = MinerStatisticsRule(savedminer, minerstats, ruleparms)
        if rule.isbroken():
            broken += rule.brokenrules
    return broken

def add_entry_for_rule(entries, rule):
    cmd_restart = MinerCommand('restart', '')
    if rule.action == 'alert':
        entries.addalert(RULES.addalert(RULES.app.stamp(rule.parameter)))
    elif rule.action == 'restart':
        entries.add(QueueName.Q_RESTART, RULES.app.createmessagecommand(rule.miner, cmd_restart))
        entries.addalert(RULES.addalert(RULES.app.stamp('Restarted {0}'.format(rule.miner.name))))
    else:
        RULES.app.logerror('did not process broken rule {0}'.format(rule.parameter))

def make_log_from_rule(rule):
    log = MinerLog()
    log.createdate = datetime.datetime.utcnow()
    log.minerid = rule.miner.key()
    log.minername = rule.miner.name
    log.action = rule.parameter
    return log

def when_statisticsupdated(channel, method, properties, body):
    '''when miner stats are pulled from miner...'''
    print("[{0}] Received miner stats".format(RULES.app.now()))
    try:
        msg = RULES.app.messagedecodeminerstats(body)
        entries = dorules(msg.miner, msg.minerstats, msg.minerpool)
        RULES.app.enqueue(entries)
    except json.decoder.JSONDecodeError as jex:
        RULES.app.logexception(jex)
        RULES.app.logdebug(RULES.app.exceptionmessage(jex))
        RULES.app.logdebug(utils.safestring(body))
    except BaseException as ex:
        RULES.app.logexception(ex)
        RULES.app.logdebug(RULES.app.exceptionmessage(ex))
        RULES.app.logdebug(utils.safestring(body))

def dorules(miner, minerstats, minerpool):
    '''run the rules on them'''
    RULES.alertstext = ''
    entries = rules(miner, minerstats, minerpool)
    if RULES.alertstext:
        print(Fore.RED + RULES.alertstext)
    print("Rules executed for {0}".format(miner.name))
    return entries

def main():
    if RULES.app.isrunnow:
        for (miner, stats, pool) in RULES.app.getminerstatscached():
            rules(miner, stats, pool)
        RULES.app.shutdown()
    else:
        RULES.listeningqueue = RULES.app.listen_to_broadcast(QueueName.Q_STATISTICSUPDATED, when_statisticsupdated)

if __name__ == "__main__":
    main()
