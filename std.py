from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
from talon import app, ctrl, clip, ui, applescript
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string
from .utils import parse_words_as_integer, optional_numerals, text, delay, tell_hammerspoon_osa, string_capture, repeat_function, no_prefix_numerals, tell_alfred_flow, press_if, no_prefix_optional_numerals
from .misc.repeat import set_again, againKey
from .vocab import add_vocab

NEXT_TAB_KEY = 'ctrl-tab'
PREV_TAB_KEY = 'ctrl-shift-tab'

# cleans up some Dragon output from <dgndictation>
mapping = {
    'semicolon': ';',
    'new-line': '\n',
    'new-paragraph': '\n\n',
}
# used for auto-spacing
punctuation = set('.,-!?')

def parse_word(word):
    word = str(word).lstrip('\\').split('\\', 1)[0]
    word = mapping.get(word, word)
    return word

def join_words(words, sep=' '):
    out = ''
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += word
    return out

def parse_words(m):
    return list(map(parse_word, m.dgndictation[0]._words))

def insert(s):
    Str(s)(None)

def text(m):
    insert(join_words(parse_words(m)).lower())

def click_elem_by_query(m):
    my_words = string_capture(m)
    # print('wtf ' + my_words)
    result = tell_hammerspoon_osa(f"clickElemInCurrentApp('{my_words}', true)")

def word(m):
    text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
    insert(text.lower())

# def surround(by):
#     def func(i, word, last):
#         if i == 0: word = by + word
#         if last: word += by
#         return word
#     return func

# def rot13(i, word, _):
#     out = ''
#     for c in word.lower():
#         if c in string.ascii_lowercase:
#             c = chr((((ord(c) - ord('a')) + 13) % 26) + ord('a'))
#         out += c
#     return out

# # better formatters - https://github.com/anonfunc/talon-user/blob/ad146e2411745b24817377c325ead6cfc8c9b9db/text/formatters.py
# formatters = {
#     'dunder': (True,  lambda i, word, _: '__%s__' % word if i == 0 else word),
#     'camel':  (True,  lambda i, word, _: word if i == 0 else word.capitalize()),
#     'snake':  (True,  lambda i, word, _: word if i == 0 else '_'+word),
#     'smash':  (True,  lambda i, word, _: word),
#     # spinal or kebab?
#     'kebab':  (True,  lambda i, word, _: word if i == 0 else '-'+word),
#     # 'sentence':  (False, lambda i, word, _: word.capitalize() if i == 0 else word),
#     'title':  (False, lambda i, word, _: word.capitalize()),
#     'caps': (False, lambda i, word, _: word.upper()),
#     'dubstring': (False, surround('"')),
#     'string': (False, surround("'")),
#     'padded': (False, surround(" ")),
#     'rot-thirteen':  (False, rot13),
# }
# def FormatText(m):
#     fmt = []
#     for w in m._words:
#         if isinstance(w, Word):
#             fmt.append(w.word)
#     try:
#         words = parse_words(m)
#     except AttributeError:
#         return
#         # # transform selected text - doesn't work well in vscode
#         # with clip.capture() as s:
#         #     press('cmd-c')
#         # words = s.get().split(' ')
#         # if not words:
#         #     return

#     tmp = []
#     spaces = True
#     for i, word in enumerate(words):
#         word = parse_word(word)
#         for name in reversed(fmt):
#             smash, func = formatters[name]
#             word = func(i, word, i == len(words)-1)
#             spaces = spaces and not smash
#         tmp.append(word)
#     words = tmp

#     sep = ' '
#     if not spaces:
#         sep = ''
#     Str(sep.join(words))(None)

def copy_bundle(m):
    bundle = ui.active_app().bundle
    clip.set(bundle)
    app.notify('Copied app bundle', body='{}'.format(bundle))

def alfred_paste_num(num):
    script = f'tell application id "com.runningwithcrayons.Alfred" to run trigger "paste" in workflow "clippastes" with argument "{num}"'
    # print(script)
    ret = applescript.run(script)
    if ret:
        return ffi.string(ret).decode('utf8')
        
def alfred_paste(m):
    clip_num = parse_words_as_integer(m._words[2:])

    if clip_num is None:
        return
    set_again('ctrl-alt-cmd-shift-v')
    return alfred_paste_num(clip_num)

def learn_selection(_):
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    words = s.get().split()
    add_vocab(words)
    tell_hammerspoon_osa(f"showQuickMessage('Learned: {words}')")
    # print("Learned " + words)

def set_theme(is_light):
    mode = 'light' if is_light == 1 else 'dark'
    tell_hammerspoon_osa(f"toggleDarkModeApp('{mode}')")

ctx = Context('input')
ctx.keymap({
    # 'say <dgndictation> [over]': text,
    # 'sentence <dgndictation> [over]': sentence_text,
    # 'phrase <dgndictation> [over]': sentence_text,
    # 'comma <dgndictation> [over]': [', ', text],
    # 'period <dgndictation> [over]': ['. ', sentence_text],
    # 'more <dgndictation> [over]': [' ', text],
    # 'word <dgnwords>': word,

    # '(%s)+ [<dgndictation>]' % (' | '.join(formatters)): FormatText,

    # more keys and modifier keys are defined in basic_keys.py
    
    'slap': [Key('cmd-right enter')],
    # 'upslap': [Key('cmd-left enter up')],
    'question [mark]': '?',
    'tilde': '~',
    '(bang | exclamation point)': '!',
    'dollar [sign]': '$',
    'down score': '_',
    'colon': ':',
    'swipe': ', ',
    'coalgap': ': ',
    '(dot dot | dotdot | doodle)': '..',
    'magic': Key('f19'),
    # "magic [<dgndictation>]": [Key("f19"), press_if("f19", '(?!magic)$')],
    '(paren | left paren | leap | laip)': '(', '(rparen | are paren | right paren | raip)': ')',
    '(brace | left brace | lace)': '{', '(rbrace | are brace | right brace | race)': '}',
    '(angle | left angle | less than | langle)': '<', '(are angle | right angle | greater than | rangle)': '>',
    '(bracket | square | L square | left square | left bracket | lack)': '[', '(are bracket | R square | right square | right bracket | rack)': ']',
    '(star | asterisk)': '*',
    '(pound | hash [sign] | number sign)': '#',
    'percent [sign]': '%',
    '(caret | carrot)': '^',
    'at sign': '@',
    '(and sign | ampersand | amper)': '&',
    'pipe': '|',

    '(dubquote | double quote)': '"',
    'triple quote': "'''",
    'cd': 'cd ',
    'cd talon home': 'cd {}'.format(TALON_HOME),
    'cd talon user': 'cd {}'.format(TALON_USER),
    'cd talon plugins': 'cd {}'.format(TALON_PLUGINS),

    # 'run make (durr | dear)': 'mkdir ',
    # 'run get': 'git ',
    # 'run get (R M | remove)': 'git rm ',
    # 'run get add': 'git add ',
    # 'run get bisect': 'git bisect ',
    # 'run get branch': 'git branch ',
    # 'run get checkout': 'git checkout ',
    # 'run get clone': 'git clone ',
    # 'run get commit': 'git commit ',
    # 'run get diff': 'git diff ',
    # 'run get fetch': 'git fetch ',
    # 'run get grep': 'git grep ',
    # 'run get in it': 'git init ',
    # 'run get log': 'git log ',
    # 'run get merge': 'git merge ',
    # 'run get move': 'git mv ',
    # 'run get pull': 'git pull ',
    # 'run get push': 'git push ',
    # 'run get rebase': 'git rebase ',
    # 'run get reset': 'git reset ',
    # 'run get show': 'git show ',
    # 'run get status': 'git status ',
    # 'run get tag': 'git tag ',
    # 'run (them | vim)': 'vim ',
    # 'run L S': 'ls\n',
    # 'dot pie': '.py',
    # 'run make': 'make\n',
    # 'run jobs': 'jobs\n',

    # 'const': 'const ',
    # 'static': 'static ',
    # 'tip pent': 'int ',
    # 'tip char': 'char ',
    # 'tip byte': 'byte ',
    # 'tip pent 64': 'int64_t ',
    # 'tip you went 64': 'uint64_t ',
    # 'tip pent 32': 'int32_t ',
    # 'tip you went 32': 'uint32_t ',
    # 'tip pent 16': 'int16_t ',
    # 'tip you went 16': 'uint16_t ',
    # 'tip pent 8': 'int8_t ',
    # 'tip you went 8': 'uint8_t ',
    # 'tip size': 'size_t',
    # 'tip float': 'float ',
    # 'tip double': 'double ',

    # 'args': ['()', Key('left')],
    # 'index': ['[]', Key('left')],
    # 'block': [' {}', Key('left enter enter up tab')],
    # 'empty array': '[]',
    # 'empty dict': '{}',

    # 'state (def | deaf | deft)': 'def ',
    # 'state else if': 'elif ',
    # 'state if': 'if ',
    # 'state else if': [' else if ()', Key('left')],
    # 'state while': ['while ()', Key('left')],
    # 'state for': ['for ()', Key('left')],
    # 'state for': 'for ',
    # 'state switch': ['switch ()', Key('left')],
    # 'state case': ['case \nbreak;', Key('up')],
    # 'state goto': 'goto ',
    # 'state import': 'import ',
    # 'state class': 'class ',

    # 'state include': '#include ',
    # 'state include system': ['#include <>', Key('left')],
    # 'state include local': ['#include ""', Key('left')],
    # 'state type deaf': 'typedef ',
    # 'state type deaf struct': ['typedef struct {\n\n};', Key('up'), '\t'],

    # 'comment see': '// ',
    # 'comment py': '# ',

    # 'word queue': 'queue',
    # 'word eye': 'eye',
    # 'word bson': 'bson',
    # 'word iter': 'iter',
    # 'word no': 'NULL',
    # 'word cmd': 'cmd',
    # 'word dup': 'dup',
    # 'word streak': ['streq()', Key('left')],
    # 'word printf': 'printf',
    # 'word (dickt | dictionary)': 'dict',
    # 'word shell': 'shell',

    # 'word talon': 'talon',
    # 'word Point2d': 'Point2d',
    # 'word Point3d': 'Point3d',
    # 'title Point': 'Point',
    # 'word angle': 'angle',

    # 'dunder in it': '__init__',
    # 'self taught': 'self.',
    # 'dickt in it': ['{}', Key('left')],
    # 'list in it': ['[]', Key('left')],
    # 'string utf8': "'utf8'",
    # 'state past': 'pass',

    # 'plus': '+',
    # 'arrow': '->',
    # 'call': '()',
    # 'indirect': '&',
    # 'dereference': '*',
    '(op equals | assign)': ' = ',
    'op (minus | subtract)': ' - ',
    'op (plus | add)': ' + ',
    'op (times | multiply)': ' * ',
    'op divide': ' / ',
    'op mod': ' % ',
    '[op] (minus | subtract) equals': ' -= ',
    '[op] (plus | add) equals': ' += ',
    '[op] (times | multiply) equals': ' *= ',
    '[op] divide equals': ' /= ',
    '[op] mod equals': ' %= ',

    '(op | is) greater [than]': ' > ',
    '(op | is) less [than]': ' < ',
    '(op | is) equal': ' == ',
    '(op | is) not equal': ' != ',
    '(op | is) greater [than] or equal': ' >= ',
    '(op | is) less [than] or equal': ' <= ',
    '(op (power | exponent) | to the power [of])': ' ** ',
    'op and': ' && ',
    'op or': ' || ',
    'trickle': ' === ',
    '(ranqual | nockle)': ' !== ',

    # '[op] (logical | bitwise) and': ' & ',
    # '[op] (logical | bitwise) or': ' | ',
    # '(op | logical | bitwise) (ex | exclusive) or': ' ^ ',
    # '[(op | logical | bitwise)] (left shift | shift left)': ' << ',
    # '[(op | logical | bitwise)] (right shift | shift right)': ' >> ',
    # '(op | logical | bitwise) and equals': ' &= ',
    # '(op | logical | bitwise) or equals': ' |= ',
    # '(op | logical | bitwise) (ex | exclusive) or equals': ' ^= ',
    # '[(op | logical | bitwise)] (left shift | shift left) equals': ' <<= ',
    # '[(op | logical | bitwise)] (right shift | shift right) equals': ' >>= ',

    # 'shebang bash': '#!/bin/bash -u\n',
    'unbox': Key('cmd-shift-t'),
    'new window': Key('cmd-n'),
    'next window': Key('cmd-`'),
    'last window': Key('cmd-shift-`'),
    # move window to this space
    '[move] window [to] space': Key('cmd-alt-ctrl-f9'),
    # move to space where window is
    '[move] space [to] window': Key('cmd-alt-ctrl-f10'),
    'space left': Key('ctrl-left'),
    'space right': Key('ctrl-right'),
    'next app': Key('cmd-tab'),
    'last app': Key('cmd-shift-tab'),
    'new tab': Key('cmd-t'),
    '(next tab | necktie | neck tap)': [Key(NEXT_TAB_KEY), set_again(NEXT_TAB_KEY, PREV_TAB_KEY)],
    '(last tab | bowtie)': [Key(PREV_TAB_KEY), set_again(PREV_TAB_KEY, NEXT_TAB_KEY)],
    
    "theme dark": lambda m: set_theme(0),
    "(theme light | day mode)": lambda m: set_theme(1),
    "(dark | night) mode": lambda m: set_theme(0),
    
    "any complete [<dgndictation>++]": [lambda m: tell_hammerspoon_osa('anyComplete()'), delay(0.25), text],
    "google": lambda m: tell_alfred_flow('net.deanishe.alfred-searchio', 'google'),
    "(duck duck | daduck)": lambda m: tell_alfred_flow('net.deanishe.alfred-searchio', 'ddg'),
    "my downloads": lambda m: tell_alfred_flow('com.sztoltz.recentitems', 'dow'),
    "[my] hotel": lambda m: tell_alfred_flow('in.johngrish.alfred-hotel', 'show'),
    "task manager": lambda m: tell_alfred_flow('com.vitorgalvao.alfred.processcontrol', 'top'),
    "start synergy": lambda m: tell_alfred_flow('er.kakamaika.clicknotif', 'startsynergy'),
    "stop synergy": lambda m: tell_alfred_flow('er.kakamaika.clicknotif', 'stopsynergy'),
    "term (restart)": againKey('ctrl-alt-space'),
    "learn (selection | this)": learn_selection,
    'menu (click | search) [<dgndictation>+]': [againKey('ctrl-alt-cmd-shift-a'), text],
    'touch <dgndictation>+': click_elem_by_query,
    'my click [<dgndictation>++]': [againKey('ctrl-alt-cmd-shift-1'), text],
    '(shortcat | short cap | shortcut)': Key('ctrl-alt-cmd-shift-f7'),
    '(channel)': Key('cmd-k'),
    # 'dash <dgndictation> [over]': [Key('ctrl-alt-cmd-f12'), text],
    # '(dash (sell | selection))': Key('ctrl-alt-cmd-shift-;'),
    '[my] (paste | park) with <dgndictation>+ [yes]': [againKey('ctrl-alt-cmd-shift-v'), text, delay(0.1), press_if("enter", "yes$")],
    '(my (paste | park))': againKey('ctrl-alt-cmd-shift-v'),
    '(my (paste | park))' + optional_numerals: alfred_paste,
    "(alfred | launch | launcher) [<dgndictation>+] [yes]": [againKey("cmd-space"), delay(0.4), text, delay(0.1), press_if("enter", "yes$")],
    "(repo[s]) [<dgndictation>++] [over]": [againKey("cmd-shift-ctrl-alt-r"), delay(0.4), text],
    '(toggle bluetooth)': Key('ctrl-alt-cmd-b'),
    '(toggle invert)': lambda m: tell_hammerspoon_osa(f'toggleAutoInvert()'),
    '(fast click)': lambda m: tell_hammerspoon_osa(f'clickNotification()'),
    # 'app search [<dgndictation>]': [againKey('ctrl-alt-cmd-shift-f8'), text],
    'app search [<dgndictation>++]': [Key('ctrl-alt-cmd-shift-f8'), delay(0.25), text, set_again('ctrl-alt-cmd-shift-f8')],
    # 'next space': againKey('cmd-alt-ctrl-right'),
    # '(last | preev) space': againKey('cmd-alt-ctrl-left'),

    # 'scroll down': [Key('down')] * 30,
    # 'scroll up': [Key('up')] * 30,
    'scroll down': [Key('down')] * 30,
    'scroll up': [Key('up')] * 30,
    
    no_prefix_numerals + '(before)': [
        Key("left shift-right left alt-left alt-right"),
        repeat_function(-1, 'alt-left'),
        set_again('alt-left', 'alt-right')
    ],
    no_prefix_numerals + '(after)': [
        Key("right shift-left right alt-right alt-left"),
        repeat_function(-1, 'alt-right'),
        set_again('alt-right', 'alt-left')
    ],

    no_prefix_numerals + '(befores | be force)': [
        Key("left shift-right left alt-left alt-right"),
        repeat_function(-1, 'alt-shift-left'),
        # set_again('alt-shift-left', 'alt-shift-right')
    ],
    no_prefix_numerals + 'afters': [
        Key("right shift-left right alt-right alt-left"),
        repeat_function(-1, 'alt-shift-right'),
        # set_again('alt-shift-right', 'alt-shift-left')
    ],

    'delete' + no_prefix_numerals + '(befores | be force)': [
        Key("left shift-right left alt-left alt-right"),
        repeat_function(-1, 'alt-shift-left'),
        Key('delete'),
        # set_again('alt-shift-left delete', 'alt-shift-right delete')
    ],
    'delete' + no_prefix_numerals + 'afters': [
        Key("right shift-left right alt-right alt-left"),
        repeat_function(-1, 'alt-shift-right'),
        Key('delete'),
        # set_again('alt-shift-right delete', 'alt-shift-left delete')
    ],

    # 'copy active bundle': copy_bundle,
})