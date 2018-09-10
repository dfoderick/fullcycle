'''Mining Rules'''
from domain.mining import Miner, MinerStatistics

class RuleParameters(object):
    '''configurable parameters for rules'''
    def __init__(self, minertype, hashlimit, controllertemplimit, boardtemplimit, restartaftersec, maxtempreset=None):
        self.minertype = minertype
        self.hashlimit = hashlimit
        self.controllertemplimit = controllertemplimit
        self.boardtemplimit = boardtemplimit
        self.restartaftersec = restartaftersec
        self.maxtempreset = maxtempreset

class BrokenRule(object):
    '''broken rules'''
    def __init__(self, miner, action, parameter):
        self.miner = miner
        self.action = action
        self.parameter = parameter
    def __str__(self):
        return 'broke {0}:{1} {2}'.format(self.miner.name, self.action, self.parameter)

class MinerStatisticsRule(object):
    '''Rule for evaluating miner statistics'''

    def __init__(self, miner: Miner, statistics: MinerStatistics, ruleparameters: RuleParameters):
        self.miner = miner
        self.statistics = statistics
        self.ruleparameters = ruleparameters
        self.brokenrules = []

    def hasreading(self, reading):
        '''True when the reading is not empty'''
        if reading is None:
            return False
        if reading:
            return False
        return True

    def hasreading_num(self, reading):
        '''True when the reading is numeric and not empty'''
        if reading is None:
            return False
        if reading == 0:
            return False
        if isinstance(reading, int):
            return True
        if isinstance(reading, float):
            return True
        return False

    def has_reboot_rule(self):
        return any(therule.action == 'restart' and therule.parameter == 'reboot' for therule in self.brokenrules)

    def addbrokenrule(self, rule):
        if rule.action == 'restart':
            if not self.has_reboot_rule():
                self.brokenrules = [therule for therule in self.brokenrules if therule.action != 'restart']
                self.brokenrules.append(rule)
        else:
            self.brokenrules.append(rule)

    def isbroken(self):
        '''true when the rule is broken'''
        self.brokenrules = []
        if self.miner.miner_type != self.ruleparameters.minertype:
            return False

        if self.hasreading_num(self.statistics.currenthash):
            if self.statistics.currenthash < self.ruleparameters.hashlimit:
                self.brokenrules.append(BrokenRule(self.miner, 'alert', 'on {0} low hash {1} below {2}'.format(self.miner.name, self.statistics.currenthash, self.ruleparameters.hashlimit)))
                if self.statistics.elapsed > self.ruleparameters.restartaftersec:
                    self.addbrokenrule(BrokenRule(self.miner, 'restart', 'restart'))
                    self.addbrokenrule(BrokenRule(self.miner, 'alert', 'restarting {0} '.format(self.miner.name)))

        if self.hasreading_num(self.statistics.controllertemp):
            if self.statistics.controllertemp and self.statistics.controllertemp > self.ruleparameters.controllertemplimit:
                self.addbrokenrule(BrokenRule(self.miner, 'alert', 'on {0} controller temp {1} exceeded {2}'.format(self.miner.name, self.statistics.controllertemp, self.ruleparameters.controllertemplimit)))

        if self.hasreading_num(self.statistics.tempboardmax()):
            if self.statistics.tempboardmax() > self.ruleparameters.boardtemplimit:
                self.addbrokenrule(BrokenRule(self.miner, 'alert', 'on {0} board temp {1} exceeded {2}'.format(self.miner.name, self.statistics.tempboardmax(), self.ruleparameters.boardtemplimit)))
            if self.ruleparameters.maxtempreset and self.statistics.tempboardmax() > self.ruleparameters.maxtempreset:
                if self.statistics.elapsed > self.ruleparameters.restartaftersec:
                    self.addbrokenrule(BrokenRule(self.miner, 'restart', 'reboot'))

        return len(self.brokenrules) > 0
