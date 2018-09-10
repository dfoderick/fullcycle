
import datetime

class TaskSchedule(object):
    lastrun : datetime.datetime
    start : datetime.datetime
    pending_run = False
    #default to 0 seconds means disabled
    #interval is in seconds
    interval = 0
    q = None

    def __init__(self, run_on_init=False):
        self.pending_run = run_on_init

    def is_disabled(self):
        return self.interval <= 0

    def is_time_to_run(self):
        if self.is_disabled(): return False
        now = datetime.datetime.now()
        if self.pending_run:
            self.pending_run = False
            return self.kick_it_off(True)
        if self.lastrun is None and self.start is None:
            #never run before, run now
            return self.kick_it_off(True)
        elif self.start is not None and self.lastrun is None:
            #never run before and after start time
            return self.kick_it_off(now > self.start)
        else:
            sincelast = now - self.lastrun
            if sincelast.total_seconds() > self.interval:
                return self.kick_it_off(True)
        return False

    def kick_it_off(self, dorun=False):
        if dorun:
            self.lastrun = datetime.datetime.now()
        return dorun
