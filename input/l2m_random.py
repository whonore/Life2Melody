import random
import threading
import time

DEBUG = False


class Random():
    def __init__(self, update_rate=15, debug=False):
        global DEBUG
        DEBUG = debug

        self.update_rate = update_rate

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        threading.Thread(target=self.update).start()

    def update(self):
        while True:
            self.energy = random.randint(-50, 50)
            self.disposition = random.randint(-50, 50)
            self.chaos = random.randint(-50, 50)

            if DEBUG:
                msg = ['Random update',
                       "Energy: {}".format(self.energy),
                       "Disposition: {}".format(self.disposition),
                       "Chaos: {}".format(self.chaos),
                       '']
                print('\n'.join(msg))

            time.sleep(self.update_rate)

    def get_energy(self):
        return int(self.energy)

    def get_disposition(self):
        return int(self.disposition)

    def get_chaos(self):
        return int(self.chaos)
