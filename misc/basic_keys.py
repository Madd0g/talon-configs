from talon.voice import Context, Str, press
import string
from ..utils import normalise_keys, insert

alpha_alt = 'air bat cap door each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip'.split()
# alpha_alt = 'air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale trex yank zip'.split()

f_keys = {f'F {i}': f'f{i}' for i in range(1, 13)}
# arrows are separated because 'up' has a high false positive rate
arrows = ['left', 'right', 'up', 'down']


# simple_keys = {
#     "lloyd": "left",
#     "crimp": "left",
#     "chris": "right",
#     "jeep": "up",
#     "doom": "down",
#     "dune": "down",
#     "junk": "backspace",
#     "backspace": "backspace",
#     "forward delete": "delete",
#     "scrap": "delete",
#     "spunk": "delete",
#     "delete": "delete",
#     "skoosh": "space",
#     "space": "space",
#     "tarp": "tab",
#     "tab": "tab",
#     "shock": "enter",
#     "enter": "enter",
#     "randall": "escape",
#     "escape": "escape",
#     "home": "home",
#     "pagedown": "pagedown",
#     "pageup": "pageup",
#     "end": "end",
# }

simple_keys = normalise_keys(
    {
    }
)

alternate_keys = {
    'delete': 'backspace',
    'forward delete': 'delete',
}
symbols = normalise_keys(
    {
        # NOTE:  This should only contain symbols that do not require any modifier
        # keys to press on a standard US keyboard layout. Commands for keys that do
        # require modifiers (e.g. ``"caret": "^"`) should belong in
        # ``text/symbol.py``.
        # "(crimp | lloyd)": "left",
        # "chris": "right",
        "jeep": "up",
        # "( dune | doom )": "down",
        '(box)': 'x',
        '(far)': 'f',
        '(king)': 'k',
        '(gone)': 'g',
        '(jik)': 'j',
        '(ice)': 'i',
        # 'green': 'g',
        'hope': 'h',
        '(sharp)': 's',
        # 'door': 'd',
        'mad': 'm',
        # 'dip': 'd',
        # 'sip': 's',
        '(tango | tea)': 't',
        # 'peach': 'p',
        'queen': 'q',
        '(oy|oil|awsh)': 'o',
        "( backspace | junk )": "backspace",
        "(delete | forward delete | dell)": "delete",
        "(space)": "space",
        "(untab | untarp | tug | left indent)": "shift-tab",
        "(tab | tarp)": "tab",
        "( enter | oozee | use )": "enter",
        "( randall | escape | scape )": "escape",
        "pagedown": "pagedown",
        "pageup": "pageup",
        "(home)": "home",
        "(end | push)": "end",
        "(tick | back tick)": "`",
        "(comma | ,)": ",",
        "(dot)": ".",
        "(semicolon | semi)": ";",
        "(quote | quatchet)": "'",
        "(slash | forward slash)": "/",
        "backslash": "\\",
        "(minus | dash)": "-",
        "(equals | smaqual)": "=",
  }
)

# symbols = {
#     'back tick': '`',
#     'comma': ',',
#     'dot': '.', 'period': '.',
#     'semi': ';', 'semicolon': ';',
#     'quote': "'",
#     'untrex': "X",
#     'L square': '[', 'left square': '[', 'square': '[',
#     'R square': ']', 'right square': ']',
#     'forward slash': '/', 'slash': '/',
#     'backslash': '\\',
#     'minus': '-', 'dash': '-',
#     'equals': '=',
# }
modifiers = {
    'command': 'cmd',
    'kemmed': 'cmd',
    'control': 'ctrl',
    'shift': 'shift',
    'alt': 'alt',
    'option': 'alt',
}

alphabet = dict(zip(alpha_alt, string.ascii_lowercase))
digits = {str(i): str(i) for i in range(10)}
simple_keys = {k: k for k in simple_keys}
arrows = {k: k for k in arrows}
keys = {}
keys.update(f_keys)
keys.update(simple_keys)
keys.update(alternate_keys)
keys.update(symbols)

# map alnum and keys separately so engine gives priority to letter/number repeats
keymap = keys.copy()
keymap.update(arrows)
keymap.update(alphabet)
keymap.update(digits)

def insert(s):
    Str(s)(None)

def get_modifiers(m):
    try:
        return [modifiers[mod] for mod in m['basic_keys.modifiers']]
    except KeyError:
        return []

def get_keys(m):
    groups = ['basic_keys.keys', 'basic_keys.arrows', 'basic_keys.digits', 'basic_keys.alphabet']
    for group in groups:
        try:
            return [keymap[k] for k in m[group]]
        except KeyError: pass
    return []

def uppercase_letters(m):
    insert(''.join(get_keys(m)).upper())

def press_keys(m):
    mods = get_modifiers(m)
    keys = get_keys(m)
    if mods:
        press('-'.join(mods + [keys[0]]))
        keys = keys[1:]
    for k in keys:
        press(k)

ctx = Context('basic_keys')
ctx.keymap({
    '(uppercase | ship | sky) {basic_keys.alphabet}+ [(lowercase | sunk)]': uppercase_letters,
    '{basic_keys.modifiers}* {basic_keys.alphabet}+': press_keys,
    '{basic_keys.modifiers}* {basic_keys.digits}+': press_keys,
    '{basic_keys.modifiers}* {basic_keys.keys}+': press_keys,
    '(go | {basic_keys.modifiers}+) {basic_keys.arrows}+': press_keys,
})
ctx.set_list('alphabet', alphabet.keys())
ctx.set_list('arrows', arrows.keys())
ctx.set_list('digits', digits.keys())
ctx.set_list('keys', keys.keys())
ctx.set_list('modifiers', modifiers.keys())
