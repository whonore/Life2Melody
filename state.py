import random
import threading
import time

class LifeState():
    def __init__(self, inputs):
        self.update_rate = 2
        
        self.energy = 0
        self.chaos = 0
        self.disposition = 0
        
        self.inputs = inputs
        
        threading.Thread(target=self.update).start()
        
    def update(self):
        print('Top state')
        while True:
            for input in self.inputs:
                self.energy += input.get_energy_change()
                self.chaos += input.get_chaos_change()
                self.disposition += input.get_disposition_change()
            print('Updating state', self.energy, self.chaos, self.disposition)
            time.sleep(self.update_rate)
            
    def get_tempo(self):
        tempo = random.randint(40, 80)
        return tempo
        
    def get_key(self):
        root = random.randint(0, 11)
        scale = random.randint(0, 1)
        return (root, scale)
        
    def get_octave(self):
        octave = random.randint(-1, 1)
        return octave
        
    def get_volume(self):
        volume = random.randint(80, 127)
        return volume
        
