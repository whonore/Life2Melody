import random
import threading
import time

DEBUG = False


def clamp(val, min, max): return sorted((val, min, max))[1]


class Updown():
    def __init__(self, update_rate=4, debug=False):
        global DEBUG
        DEBUG = debug

        self.update_rate = update_rate

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        self.de = random.choice((-1, 1)) * random.randint(1, 3)
        self.dd = random.choice((-1, 1)) * random.randint(1, 3)
        self.dc = random.choice((-1, 1)) * random.randint(1, 3)

        threading.Thread(target=self.update).start()

    def update(self):
        while True:
            self.energy += self.de
            self.disposition += self.dd
            self.chaos += self.dc

            self.energy = clamp(self.energy, -50, 50)
            self.disposition = clamp(self.disposition, -50, 50)
            self.chaos = clamp(self.chaos, -50, 50)

            if self.energy in (-50, 50):
                self.de *= -1
            if self.disposition in (-50, 50):
                self.dd *= -1
            if self.chaos in (-50, 50):
                self.dc *= -1

            if DEBUG:
                msg = ['Updown update',
                       "Energy: {} (+ {})".format(self.energy, self.de),
                       "Disposition: {} (+ {})".format(self.disposition, self.dd),
                       "Chaos: {} (+ {})".format(self.chaos, self.dc),
                       '']
                print('\n'.join(msg))

            time.sleep(self.update_rate)

    def get_energy(self):
        return int(self.energy)

    def get_disposition(self):
        return int(self.disposition)

    def get_chaos(self):
        return int(self.chaos)
