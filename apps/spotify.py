from talon.voice import Context, Key, Str, press
import string

ctx = Context('spotify', bundle='com.spotify.client')


def parse_word(word):
    word = word.lstrip('\\').split('\\', 1)[0]
    return word


def search_for(m):
    press('cmd-l')
    tmp = [str(s).lower() for s in m.dgndictation[0]._words]
    words = [parse_word(word) for word in tmp]
    Str(' '.join(words))(None)


keymap = {
    'search for [<dgndictation>]': search_for,
    'make new playlist': Key('cmd-n'),
    'make new playlist folder': Key('cmd-shift-n'),
    'seek forward': Key('cmd-shift-right'),
    'seek backward': Key('cmd-shift-left'),
    '(more volume | volume up | increase volume)': Key('cmd-up'),
    '(less volume | volume down | decrease volume)': Key('cmd-down'),
    '[toggle] shuffle': Key('cmd-s'),
    '[toggle] repeat': Key('cmd-r'),
    'filter': Key('cmd-f'),
    'mute volume': Key('cmd-shift-down'),
    'max volume': Key('cmd-shift-up'),
}

ctx.keymap(keymap)
