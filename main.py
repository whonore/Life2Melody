import argparse

from state import LifeState
from music import Player


def main(inmods, debug):
    inputs = []
    for mod in inmods:
        modname = 'input.l2m_' + mod
        inputs.append(getattr(__import__(modname, globals(), locals(),
                                         [mod.capitalize()], -1),
                              mod.capitalize())(debug=debug))

    state = LifeState(inputs, debug=debug)
    player = Player(state, debug=debug)
    player.play_song()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inmods', nargs='*')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()
    main(args.inmods, args.debug)
