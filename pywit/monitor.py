import time
from .interface import SteemExplorer
from .logger import Logger
from .config import Configuration

class WitnessMonitor():
    def __init__(self, stm: SteemExplorer, update_time=300, missed=5, backup=''):
        self.stm = stm
        self.conf = stm.conf
        self.log = stm.log
        self.missed = missed
        self.t = update_time
        if backup:
            self.b = backup
        else:
            self.b = False

    def monitor_witness(self):
        self.log.add_func("WitnessMonitor:monitor_witness")
        if self.stm.locked():
            if not self.stm.unlock_wallet():
                print("You must unlock your wallet to monitor witness.")
                return
        last_missed = self.stm.get_missed()
        logstr = "Total blocks missed: {}".format(last_missed)
        self.log.log(logstr, 1)
        if self.b:
            logstr = "Switching to backup key at {} missed blocks.".format(self.missed)
            self.log.log(logstr, 1)
        else:
            logstr = "Disabling witness key at {} missed blocks.".format(self.missed)
            self.log.log(logstr, 1)
        session_missed = 0
        while True:
            try:
                m = self.stm.get_missed()
                logstr = "Updating... {} missed blocks.".format(m)
                self.log.log(logstr, 1)
                if m > last_missed:
                    session_missed += (m - last_missed)
                    last_missed = m
                    logstr = "New missed block: {} total, {} session.".format(m, session_missed)
                    self.log.log(logstr, 1)
                    if session_missed >= self.missed:
                        if self.kill_witness(session_missed):
                            self.log.pop_func()
                            return
                        else:
                            session_missed = 0
                            logstr = "Switched to backup key {}".format(self.b)
                            self.log.log(logstr, 1)
                            self.b = False
                time.sleep(self.t)
            except KeyboardInterrupt:
                self.log.pop_func()
                print(" ")
                return

    #Returns true if witness disabled, which returns from the monitoring loop
    def kill_witness(self, session_missed):
        self.log.add_func("WitnessMonitor:kill_witness")
        if self.b:
            self.stm.update(key=self.b)
            logstr = "Switching to backup key, {} blocks have been missed this session.".format(session_missed)
            self.log.log(logstr, 0)
            #notify you somehow?

            self.log.pop_func()
            return False
        else:
            self.stm.disable_witness()
            logstr = "Disabling witness key, {} blocks have been missed this session.".format(session_missed)
            self.log.log(logstr, 0)
            #figure out how to notify?

            self.log.pop_func()
            return True
