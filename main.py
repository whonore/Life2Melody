import sys
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
    inmods = sys.argv[1:]
    debug = ('-d' in inmods)

    if debug:
        inmods.remove('-d')

    main(inmods, debug)
