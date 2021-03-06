from __future__ import division

try:
    import Queue as queue
except ImportError:
    import queue
import random
import threading
import time

from pygame import midi

BASE_REST_CHANCE = 0.05
PIANO = 0
CELLO = 42
CONSONANT = (0, 2, 4, 5)  # root, 3rd, 5th, 6th
DISSONANT = (1, 3, 6)  # 2nd, 4th, 7th
SCALES = ((0, 2, 4, 5, 7, 9, 11),  # Major
          (0, 2, 3, 5, 7, 9, 10),  # Dorian
          (0, 1, 3, 5, 7, 8, 10),  # Phyrgian
          (0, 2, 4, 6, 7, 9, 11),  # Lydian
          (0, 2, 4, 5, 7, 9, 10),  # Mixolydian
          (0, 2, 3, 5, 7, 8, 10),  # Minor
          (0, 1, 3, 5, 6, 8, 10))  # Locrian


class Player(object):
    def __init__(self, state, debug=False):
        self.debug = debug

        midi.init()

        self.state = state
        self.player = midi.Output(2)

        self.notes = queue.Queue()
        self.update_rate = 2  # secs

        self.tempo = 90.0  # bpm
        self.key = (0, 4)  # C mix
        self.octave = 0  # Middle
        self.volume = 100  # Velocity
        self.dissonance = 0.1
        self.length_ratio = (1, 4)  # 1:4

        self.rest_chance = BASE_REST_CHANCE

    def update(self):
        self.tempo = self.state.get_tempo(self.tempo)
        self.key = self.state.get_key(self.key)
        self.octave = self.state.get_octave(self.octave)
        self.volume = self.state.get_volume(self.volume)
        self.dissonance = self.state.get_dissonance(self.dissonance)
        self.length_ratio = self.state.get_length_ratio(self.length_ratio)

        if self.debug:
            msg = ['Music update',
                   "Tempo: {}".format(self.tempo),
                   "Key: {}".format(self.key),
                   "Octave: {}".format(self.octave),
                   "Volume: {}".format(self.volume),
                   "Dissonance: {}".format(self.dissonance),
                   "Length Ratio: {}".format(self.length_ratio),
                   '']
            print('\n'.join(msg))

        threading.Timer(self.update_rate, self.update).start()

    def play_song(self):
        self.update()

        melody_counter = 0
        harmony_counter = 0

        while True:
            duration = 60 / self.tempo
            melody_duration = duration * self.length_ratio[0]
            harmony_duration = duration * self.length_ratio[1]

            if random.random() < self.rest_chance:
                self.rest_chance = BASE_REST_CHANCE
                melody_volume = 0
            else:
                self.rest_chance += 0.005
                melody_volume = self.volume

            melody_note = self.choose_melody()
            bass_note, harmony_note = self.choose_harmony()
            harmony_volume = self.volume - 10

            melody = (PIANO,
                      melody_note,
                      melody_duration,
                      melody_volume)
            harmony = (CELLO,
                       harmony_note,
                       harmony_duration,
                       harmony_volume)
            bass = (CELLO,
                    bass_note,
                    harmony_duration,
                    harmony_volume)

            notes = []
            if melody_counter == 0:
                notes.append(melody)
            if harmony_counter == 0:
                notes.extend([bass, harmony])

            self.play_notes(notes)

            melody_counter = (melody_counter + 1) % self.length_ratio[0]
            harmony_counter = (harmony_counter + 1) % self.length_ratio[1]
            time.sleep(duration)

    def play_notes(self, notes):
        for instrument, note, duration, volume in notes:
            self.play_note(instrument, note, duration, volume)

    def play_note(self, instrument, note, duration, volume):
        self.player.set_instrument(instrument)
        self.player.note_on(note, volume)
        self.notes.put_nowait((note, volume, duration))

        threading.Thread(target=self.stop_note).start()

    def stop_note(self):
        note, _, duration = self.notes.get_nowait()
        time.sleep(duration)
        self.player.note_on(note, 0)
        self.notes.task_done()

    def choose_melody(self):
        base_note = 60 + self.key[0] + self.octave * 12

        if random.random() < self.dissonance:
            intervals = DISSONANT
        else:
            intervals = CONSONANT

        scale = SCALES[self.key[1]]
        interval = scale[random.choice(intervals)]

        note = base_note + interval

        return note

    def choose_harmony(self):
        base_note = 60 + self.key[0] + max((self.octave - 2), -2) * 12

        if random.random() < self.dissonance:
            intervals = DISSONANT
        else:
            intervals = CONSONANT

        scale = SCALES[self.key[1]]
        interval = scale[random.choice(intervals)]

        bass = base_note
        harmony = base_note + interval

        return (bass, harmony)
