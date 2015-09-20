from video import Video
from state import LifeState
from music import Player


def main():
    inputs = [Video()]
    state = LifeState(inputs)
    player = Player(state)
    player.play_song()

if __name__ == '__main__':
    main()
