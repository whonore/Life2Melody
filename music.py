import Queue
import random
import threading
import time
from pygame import midi
from state import LifeState 

class Player():
    def __init__(self, state):
        midi.init()
    
        self.notes = Queue.Queue()
        self.state = state
        self.player = midi.Output(2)
        self.update_rate = 5 # secs
        
        self.tempo = 60.0 # bpm
        self.key = (0, 0) # C maj
        self.octave = 0 # Middle
        self.volume = 100 # Velocity
        
        self.rest_chance = 0.1
        
    def update(self):
        print('Top player')
        while True:
            self.tempo = float(self.state.get_tempo())
            self.key = self.state.get_key()
            self.octave = self.state.get_octave()
            self.volume = self.state.get_volume()
            
            print('Updating player', self.tempo, self.key, self.octave, self.volume)
            
            time.sleep(self.update_rate)
            
        
    def play_song(self):
        threading.Thread(target=self.update).start()
        
        while True:
            duration = 60 / self.tempo
            note = self.choose_note()
            
            print('Playing', note, duration)
            
            notes = [(note, duration)]
            self.play_notes(notes)
        
    def play_notes(self, notes):
        for note, duration in notes:
            self.play_note(note, duration)
        self.notes.join()
        
    def play_note(self, note, duration):
        self.player.note_on(note, self.volume)
        self.notes.put_nowait((note, self.volume, duration))
        note_t = threading.Thread(target=self.stop_note)
        note_t.start()
        
    def stop_note(self):
        note, velocity, duration = self.notes.get_nowait()
        time.sleep(duration)
        self.player.note_on(note, 0)
        self.notes.task_done()
        
    def choose_note(self):
        base_note = 60 + self.octave * 12
        interval = self.key[0]
        
        note = base_note + interval
        
        return note
    
