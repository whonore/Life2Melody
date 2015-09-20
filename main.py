#import video
from state import LifeState
from music import Player


def main():
    state = LifeState([])
    player = Player(state)
    player.play_song()
    
if __name__ == '__main__':
    main()
