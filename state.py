import numpy
import random
import threading
import time

DEBUG = False

ENERGY_RANGE = (-50.0, 50.0)
DISPOSITION_RANGE = (-50.0, 50.0)
CHAOS_RANGE = (-50.0, 50.0)

TEMPO_RANGE = (60, 180)
VOLUME_RANGE = (70, 127)

# Major -> Mixolydian (-) | Lydian (-) 0
# Dorian -> Minor (-) | Mixolydian (+) 1
# Phyrgian -> Locrian (-) | Minor (+) 2
# Lydian -> Mixolydian (-) | Major (+) 3
# Mixolydian -> Dorian (-) | Major (+) 4
# Minor -> Phyrgian (-) | Dorian (+) 5
# Locrian -> Locrian (-) | Phyrgian (+) 6

SCALE_ORDER = (6, 2, 5, 1, 4, 3, 0)


def clamp(val, min, max): return sorted((val, min, max))[1]


class LifeState():
    def __init__(self, inputs, debug=False):
        global DEBUG
        DEBUG = debug

        self.update_rate = 3

        self.energy = 0
        self.disposition = 0
        self.chaos = 0

        self.inputs = inputs

        threading.Thread(target=self.update).start()

    def update(self):
        while True:
            states = [(clamp(input.get_energy(), *ENERGY_RANGE),
                       clamp(input.get_disposition(), *DISPOSITION_RANGE),
                       clamp(input.get_chaos(), *CHAOS_RANGE))
                      for input in self.inputs]
            states = zip(*states)

            if not states:
                states = [(self.energy,), (self.disposition,), (self.chaos,)]

            self.energy = numpy.mean(states[0])
            self.disposition = numpy.mean(states[1])
            self.chaos = numpy.mean(states[2])

            if DEBUG:
                msg = ['State update',
                       "Energy: {} ({})".format(self.energy, states[0]),
                       "Disposition: {} ({})".format(self.disposition, states[1]),
                       "Chaos: {} ({})".format(self.chaos, states[2]),
                       '']
                print('\n'.join(msg))

            time.sleep(self.update_rate)

    def get_tempo(self, current_tempo):  # Energy +/- Chaos
        # f(x) = {log(x + 1) * (240 - 90) / log(51) + 90 | x >= 0
        #         (e^(x + 50) - 1) * (90 - 60) / (e^50 - 1) + 60 | x <= 0}

        cur_energy = self.energy
        cur_chaos = self.chaos

        if cur_energy >= 0:
            tempo = (numpy.log10(cur_energy + 1) *
                     (TEMPO_RANGE[1] - 90) / numpy.log10(ENERGY_RANGE[1] + 1) +
                     90)
        else:
            tempo = ((numpy.exp(cur_energy + ENERGY_RANGE[1]) - 1) *
                     (90 - TEMPO_RANGE[0]) / (numpy.exp(ENERGY_RANGE[1]) - 1) +
                     60)

        tempo += cur_chaos / CHAOS_RANGE[1]

        # Tempo can only change by at most 20 bpm
        tempo_dif = tempo - current_tempo
        if abs(tempo_dif) > 20:
            sgn = tempo_dif / abs(tempo_dif)
            tempo = current_tempo + sgn * 20

        return tempo

    def get_key(self, current_key):  # Disposition
        cur_disposition = self.disposition

        d_ratio = ((cur_disposition + DISPOSITION_RANGE[1]) /
                   (DISPOSITION_RANGE[1] - DISPOSITION_RANGE[0]))

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
        elif 0.7 <= d_ratio:
            target_scale = 6

        scale_rank = SCALE_ORDER.index(current_key[1])
        if target_scale > scale_rank:
            direction = 1
        elif target_scale < scale_rank:
            direction = -1
        else:
            direction = 0

        scale = SCALE_ORDER[scale_rank + direction]

        root = 0
        return (root, scale)

    def get_octave(self, current_octave):
        octave = current_octave
        if random.random() < 0.1:
            octave = current_octave + random.choice((-1, 1))
            if abs(octave) > 1:
                octave = current_octave

        return octave

    def get_volume(self):  # Energy +/- Chaos
        cur_energy = self.energy
        cur_chaos = self.chaos

        e_ratio = ((cur_energy + ENERGY_RANGE[1]) /
                   (ENERGY_RANGE[1] - ENERGY_RANGE[0]))

        volume = e_ratio * (VOLUME_RANGE[1] - VOLUME_RANGE[0]) + VOLUME_RANGE[0]
        volume += cur_chaos / CHAOS_RANGE[1]

        return int(volume)

    def get_dissonance(self):  # Disposition
        cur_disposition = self.disposition

        d_ratio = ((cur_disposition + DISPOSITION_RANGE[1]) /
                   (DISPOSITION_RANGE[1] - DISPOSITION_RANGE[0]))

        dissonance = 0.1
        if 0 <= d_ratio < 0.1:
            dissonance = 0.2
        elif 0.9 <= d_ratio:
            dissonance = 0.05

        return dissonance

    def get_length_ratio(self):  # Energy +/- Chaos
        cur_energy = self.energy

        e_ratio = ((cur_energy + ENERGY_RANGE[1]) /
                   (ENERGY_RANGE[1] - ENERGY_RANGE[0]))

        if 0 <= e_ratio < 0.1:
            length_ratio = (1, 2)
        elif 0.1 <= e_ratio < 0.6:
            length_ratio = (1, 4)
        elif 0.6 <= e_ratio < 0.8:
            length_ratio = (1, 3)
        elif 0.8 <= e_ratio < 0.9:
            length_ratio = (1, 2)
        elif 0.9 <= e_ratio:
            length_ratio = (2, 1)

        return length_ratio
