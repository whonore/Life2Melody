import random
import threading


class Random(object):
    def __init__(self, update_rate=15, debug=False):
        self.debug = debug

        self.update_rate = update_rate  # secs

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        self.update()

    def update(self):
        self.energy = random.randint(-50, 50)
        self.disposition = random.randint(-50, 50)
        self.chaos = random.randint(-50, 50)

        if self.debug:
            msg = ['Random update',
                   "Energy: {}".format(self.energy),
                   "Disposition: {}".format(self.disposition),
                   "Chaos: {}".format(self.chaos),
                   '']
            print('\n'.join(msg))

        threading.Timer(self.update_rate, self.update)
