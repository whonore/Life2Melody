import random
import threading

import numpy as np


class Updown(object):
    def __init__(self, update_rate=4, debug=False):
        self.debug = debug

        self.update_rate = update_rate  # secs

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        self.de = random.choice((-1, 1)) * random.randint(1, 3)
        self.dd = random.choice((-1, 1)) * random.randint(1, 3)
        self.dc = random.choice((-1, 1)) * random.randint(1, 3)

        self.update()

    def update(self):
        self.energy += self.de
        self.disposition += self.dd
        self.chaos += self.dc

        self.energy = np.clip(self.energy, -50, 50)
        self.disposition = np.clip(self.disposition, -50, 50)
        self.chaos = np.clip(self.chaos, -50, 50)

        if self.energy in (-50, 50):
            self.de *= -1
        if self.disposition in (-50, 50):
            self.dd *= -1
        if self.chaos in (-50, 50):
            self.dc *= -1

        if self.debug:
            msg = ['Updown update',
                   "Energy: {} (+ {})".format(self.energy, self.de),
                   "Disposition: {} (+ {})".format(self.disposition, self.dd),
                   "Chaos: {} (+ {})".format(self.chaos, self.dc),
                   '']
            print('\n'.join(msg))

        threading.Timer(self.update_rate, self.update)
