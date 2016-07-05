from __future__ import division

import random
import threading

import numpy as np

# Major      -> Mixolydian (-) | Lydian (-) 0
# Dorian     -> Minor (-) | Mixolydian (+)  1
# Phyrgian   -> Locrian (-) | Minor (+)     2
# Lydian     -> Mixolydian (-) | Major (+)  3
# Mixolydian -> Dorian (-) | Major (+)      4
# Minor      -> Phyrgian (-) | Dorian (+)   5
# Locrian    -> Locrian (-) | Phyrgian (+)  6

SCALE_ORDER = (6, 2, 5, 1, 4, 3, 0)


class MinMax(object):
    def __init__(self, min_, max_):
        self.min = min_
        self.max = max_

    @property
    def diff(self):
        return self.max - self.min

    @property
    def minmax(self):
        return (self.min, self.max)

    def norm(self, n):
        return (n - self.min) / self.max

E_RANGE = MinMax(-50.0, 50.0)
D_RANGE = MinMax(-50.0, 50.0)
C_RANGE = MinMax(-50.0, 50.0)
T_RANGE = MinMax(60, 180)
V_RANGE = MinMax(70, 127)


class LifeState(object):
    def __init__(self, inputs, debug=False):
        self.debug = debug

        self.inputs = inputs

        self.update_rate = 3  # secs

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        self.update()

    def update(self):
        if len(self.inputs) > 0:
            ranges = zip(*(E_RANGE.minmax, D_RANGE.minmax, C_RANGE.minmax))
            states = [(input.energy,
                       input.disposition,
                       input.chaos)
                      for input in self.inputs]
            states = np.clip(states, *ranges)
            energies, dispositions, chaoses = zip(*states.tolist)

            self.energy = np.mean(energies)
            self.disposition = np.mean(dispositions)
            self.chaos = np.mean(chaoses)

            if self.debug:
                msg = ['State update',
                       "Energy: {}".format(self.energy),
                       "Disposition: {}".format(self.disposition),
                       "Chaos: {}".format(self.chaos),
                       '']
                print('\n'.join(msg))

        threading.Timer(self.update_rate, self.update).start()

    def get_tempo(self, old_tempo):  # Energy +/- Chaos
        # f(en) = {log(en + 1) * (T - 90) / log(E + 1) + 90    | en >= 0
        #         (e^(en + E) - 1) * (90 - t) / (e^E - 1) + 60 | en <= 0}
        # en = energy, E = max_energy, T = max_tempo, t = min_tempo

        energy = self.energy
        chaos = self.chaos

        if energy >= 0:
            _a = np.log10(energy + 1)
            _b = T_RANGE.max - 90
            _c = np.log10(E_RANGE.max + 1)
            _d = 90
        else:
            _a = np.exp(energy + E_RANGE.max) - 1
            _b = 90 - T_RANGE.min
            _c = np.exp(E_RANGE.max) - 1
            _d = 60

        tempo = _a * _b / _c + _d
        tempo += chaos / C_RANGE.diff

        # Tempo can only change by at most 20 bpm
        tempo = np.clip(tempo, old_tempo - 20, old_tempo + 20)

        return tempo

    def get_key(self, old_key):  # Disposition
        disposition = self.disposition

        d_ratio = D_RANGE.norm(disposition)

        if 0 <= d_ratio < 0.05:
            target_scale = 0
        elif 0.05 <= d_ratio < 0.12:
            target_scale = 1
        elif 0.12 <= d_ratio < 0.3:
            target_scale = 2
        elif 0.3 <= d_ratio < 0.4:
            target_scale = 3
        elif 0.4 <= d_ratio < 0.7:
            target_scale = random.choice((4, 5))
        elif 0.7 <= d_ratio <= 1:
            target_scale = 6

        scale_rank = SCALE_ORDER.index(old_key[1])
        direction = np.sign(target_scale - scale_rank)

        scale = SCALE_ORDER[scale_rank + direction]
        root = 0

        key = (root, scale)

        return key

    def get_octave(self, old_octave):
        octave = old_octave

        if random.random() < 0.1:
            octave = old_octave + random.choice((-1, 1))

            if abs(octave) > 1:
                octave = old_octave

        return octave

    def get_volume(self, _old_volume):  # Energy +/- Chaos
        energy = self.energy
        chaos = self.chaos

        e_ratio = E_RANGE.norm(energy)

        volume = e_ratio * (V_RANGE.diff) + V_RANGE.min
        volume += chaos / C_RANGE.diff

        return int(volume)

    def get_dissonance(self, _old_dissonance):  # Disposition
        disposition = self.disposition

        d_ratio = D_RANGE.norm(disposition)

        if 0 <= d_ratio < 0.1:
            dissonance = 0.2
        elif 0.1 <= d_ratio < 0.9:
            dissonance = 0.1
        elif 0.9 <= d_ratio <= 1:
            dissonance = 0.05

        return dissonance

    def get_length_ratio(self, _old_length_ratio):  # Energy +/- Chaos
        energy = self.energy

        e_ratio = E_RANGE.norm(energy)

        if 0 <= e_ratio < 0.1:
            length_ratio = (1, 2)
        elif 0.1 <= e_ratio < 0.6:
            length_ratio = (1, 4)
        elif 0.6 <= e_ratio < 0.8:
            length_ratio = (1, 3)
        elif 0.8 <= e_ratio < 0.9:
            length_ratio = (1, 2)
        elif 0.9 <= e_ratio <= 1:
            length_ratio = (2, 1)

        return length_ratio
