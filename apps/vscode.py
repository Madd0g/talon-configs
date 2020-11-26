from talon.voice import Context, Key, press, Str
from talon import applescript
from ..misc.basic_keys import get_keys
from ..utils import (
    parse_words_as_integer,
    repeat_function,
    optional_numerals,
    no_prefix_numerals,
    text,
    delay,
    press_if,
    string_capture,
)
from ..misc.repeat import set_again, againKey
context = Context("VSCode", bundle="com.microsoft.VSCode")

ACTION_POPUP_KEY = 'cmd-shift-a'
FILE_OPEN_KEY = "cmd-shift-o"
BACK_KEY = "cmd-alt-left"
FORWARD_KEY = "cmd-alt-right"
SELECT_LINE_UP = "cmd-shift-i"
SELECT_LINE_DOWN = "cmd-i"
CAPS_UP = "cmd-shift-alt-ctrl-up"
CAPS_DOWN = "cmd-shift-alt-ctrl-down"
CAPS_LEFT = "cmd-shift-alt-ctrl-left"
CAPS_RIGHT = "cmd-shift-alt-ctrl-right"

def jump_to_line(m):
    line_number = parse_words_as_integer(m._words[1:])

    if line_number is None:
        return

    # Zeroth line should go to first line
    if line_number == 0:
        line_number = 1

    press("cmd-l")
    Str(str(line_number))(None)
    press("enter")


def jump_tabs(m):
    line_number = parse_words_as_integer(m._words[1:])

    if line_number is None:
        return

    for i in range(0, line_number):
        press("cmd-alt-right")

def jump_to_next_word_instance(m):
    press("escape")
    press("cmd-f")
    Str(" ".join([str(s) for s in m.dgndictation[0]._words]))(None)
    press("return")


def select_lines_function(m):
    divider = 0
    for word in m._words:
        if str(word) == "until":
            break
        divider += 1
    line_number_from = int(str(parse_words_as_integer(m._words[2:divider])))
    line_number_until = int(str(parse_words_as_integer(m._words[divider + 1 :])))
    number_of_lines = line_number_until - line_number_from

    press("cmd-l")
    Str(str(line_number_from))(None)
    press("enter")
    for i in range(0, number_of_lines + 1):
        press("shift-down")
        
def fold_level(m):
    line_number = parse_words_as_integer(m._words[1:])
    if line_number is None:
        return
    press('cmd-k')
    press('cmd-' + str(line_number))

vim_dict = {
    'copy': 'y',
    
    'select': 'v',
    'change': 'c',
    'delete': 'd',
    
    'line': 'line',
    
    'until': 't',
    'till': 't',
    'including': 'f',
    'include': 'f',
    
    'in': 'i',
    'inside': 'i',
    'around': 'a',
}

def make_vim(m):
    seq = ['escape']
    act = vim_dict[m._words[0]]
    if act == None:
        return
    mov = vim_dict[m._words[1]]
    if mov == None:
        return
    
    if mov == 'line' and act == 'c':
        mov = 'c'
    elif mov == 'line' and act == 'd':
        mov = 'd'
    elif mov == 'line' and act == 'y':
        mov = 'y'
    elif mov == 'line' and act == 'v':
        act = 'V'
        mov = None

    seq.append(act)
    
    if mov != None:
        seq.append(mov)
    
    captured = get_keys(m)
    print('capt', captured)
    if captured != None and captured != '':
        seq = seq + captured
    print('vim', seq, m)

def make_vim_simple(m):
    seq = ['escape']
    act = vim_dict[m._words[0]]
    if act == None:
        return
    seq.append(act)
    amount = parse_words_as_integer(m._words[1:])
    if amount is None:
        return
    seq.append(str(amount))
    
    mov = m._words[-1:]
    keys = get_keys(m)
    seq = seq + keys
    Key(" ".join(seq))(m)
    # print('vims', seq, m)

context.set_list('vim_action', [
    'select',
    'change',
    'delete',
])

context.set_list('vim_move', [
    'line',
    'in',
    'inside',
    'around',
    'until',
    'till',
    'including',
    'include',
])

context.set_list('vim_dir', [
    '0',
    '$',
    '^',
    'h',
    'w',
    'W',
    'j',
    'k',
    'l',
    't',
    'T',
])

context.keymap(
    {
        # Selecting text
        "select line"
        + optional_numerals
        + "until"
        + optional_numerals: select_lines_function,
        # Finding text
        "find": Key("cmd-f"),
        "find next <dgndictation>": jump_to_next_word_instance,
        "fold": Key('cmd--'),
        "fold" + no_prefix_numerals: fold_level,
        "(fold all | overview)": Key('cmd-shift--'),
        # todo fold levels
        "unfold": Key('cmd-+'),
        "(unfold all | underview)": Key('cmd-shift-+'),
        "clone": Key("cmd-d"),
        # Navigation
        "line" + optional_numerals: jump_to_line,
        "Go to line": Key("cmd-l"),
        "(drag | line) up" + optional_numerals: [repeat_function(2, "alt-shift-up"), set_again("alt-shift-up", "alt-shift-down")],
        "(drag | line) down" + optional_numerals: [repeat_function(2, "alt-shift-down"), set_again("alt-shift-down", "alt-shift-up")],
        "recents [<dgndictation>]": [Key("cmd-e"), text],
        "projects [<dgndictation>]": [Key("cmd-e"), text],
        "window [<dgndictation>]": [Key("ctrl-w"), text],
        "(squash | crap)": Key("cmd-delete"),
        "(key mode | keyboard)": Key("cmd-alt-ctrl-v"),
        # "key mode": Key("alt-f3"),
        "relative ( numbers | lines )": Key("alt-f4"),
        # switch line numberings
        # "key mode": Key("cmd-alt-ctrl-v"),
        "(preev | previous) block": againKey("alt-home"),
        "next block": againKey("alt-end"),
        # Navigating Interface
        "(focus | fox) files": Key("shift-cmd-e"),
        "explore tab": Key("shift-cmd-e"),
        "search (tab | all | files)": Key("shift-cmd-f"),
        "debug tab": Key("shift-cmd-d"),
        "((hide | toggle) pane[l] | pane[l] hide)": againKey("cmd-j"),
        "(source control | git | jet) tab": Key("ctrl-shift-g"),
        "(focus | fox) (jet | git)": Key("ctrl-shift-g"),
        "extensions tab": Key("shift-cmd-x"),
        "(switch | go to file) [<dgndictation>+] [yes]": [Key(f"{FILE_OPEN_KEY}"), text, delay(0.1), press_if("enter", "yes$"), set_again(f"{FILE_OPEN_KEY}", f"{FILE_OPEN_KEY} delete down")],
        "branch [<dgndictation>++] [over]": [againKey("ctrl-alt-`"), text],
        "sync": Key("cmd-t"),
        "context [menu]": [
            Key(ACTION_POPUP_KEY),
            "Editor Context\n",
        ],
        "stage changes": [
            Key(ACTION_POPUP_KEY),
            "Stage changes\n",
        ],
        "unstage changes": [
            Key(ACTION_POPUP_KEY),
            "Unstage changes",
        ],
        "(template | snippet)": [
            againKey(ACTION_POPUP_KEY),
            "Insert Snippet\n",
        ],
        "(template | snippet) <dgndictation>+ [yes]": [
            againKey(ACTION_POPUP_KEY),
            "Insert Snippet\n",
            delay(0.2),
            text,
            press_if("enter", "yes$")
        ],
        "(symbol) <dgndictation>+ [yes]": [
            againKey('cmd-o'),
            delay(0.1),
            text,
            press_if("enter", "yes$")
        ],
        # tabbing
        # "(next tab | neck tap)": Key("ctrl-tab"),
        # "last tab": Key("ctrl-shift-tab"),
        # "stiffy": Key("cmd-alt-left"),
        # "stippy": Key("cmd-alt-right"),
        # "new file": Key("cmd-n"),
        "new file": [
            againKey(ACTION_POPUP_KEY),
            "new File Relative Current\n",
        ],
        "new file <dgndictation> [over]": [
            againKey(ACTION_POPUP_KEY),
            "new File Relative Current\n",
            delay(0.3),
            text,
        ],
        "new folder": [
            againKey(ACTION_POPUP_KEY),
            "Folder Relative Current\n",
        ],
        "new folder <dgndictation> [over]": [
            againKey(ACTION_POPUP_KEY),
            "Folder Relative Current\n",
            delay(0.3),
            text,
        ],
        "(jay slap | semi slap)": Key("alt-\\"),
        "((jay | auto) format)": againKey("cmd-alt-l"),
        "(go back)": [Key(BACK_KEY), set_again(BACK_KEY, FORWARD_KEY)],
        "(go forward)": [Key(FORWARD_KEY), set_again(FORWARD_KEY, BACK_KEY)],
        "((jay | (select | sell) line) up)": [Key(SELECT_LINE_UP), set_again(SELECT_LINE_UP, SELECT_LINE_DOWN)],
        "((jay | (select | sell) line) down)": [Key(SELECT_LINE_DOWN), set_again(SELECT_LINE_DOWN, SELECT_LINE_UP)],
        "(jay (next | neck))": [Key(CAPS_RIGHT), set_again(CAPS_RIGHT, CAPS_LEFT)],
        "(jay (preev | previous))": [Key(CAPS_LEFT), set_again(CAPS_LEFT, CAPS_RIGHT)],
        "(jay (increase | plus))": [Key(CAPS_UP), set_again(CAPS_UP, CAPS_DOWN)],
        "(jay (decrease | minus))": [Key(CAPS_DOWN), set_again(CAPS_DOWN, CAPS_UP)],
        "(jay select | select from (here | this))": againKey("alt-shift-;"),
        "(jay quotes)": againKey("cmd-'"),
        "(go reference)": Key("cmd-b"),
        "(peek reference)": Key("cmd-alt-f7"),
        "what the fuck": Key("cmd-alt-g b"), #git blame
        "fix": Key("cmd-."),
        "fix next": [Key("f2 cmd-.")],
        # "fix [this] [<dgndictation>] [over]": [Key("cmd-."), text],
        "fix (all | problems)": Key("cmd-alt-ctrl-p"),
        "cursor up": againKey("alt-cmd-up"),
        "cursor down": againKey("alt-cmd-down"),
        "slap up[per]": againKey("cmd-alt-enter"),
        "(gimme | more)": [Key("alt-up")],
        "(meg | less)": [Key("alt-down")],
        "(refactor | rename)": againKey("shift-f6"),
        # "jump" + optional_numerals: jump_tabs,
        # Menu
        "save": Key("cmd+s"),
        "open": Key("cmd+o"),
        "wide": againKey('ctrl-alt-3'),
        "unwide": againKey('ctrl-alt-4'),
        "rename file": againKey("ctrl-shift-f6"),
        "(untug | right indent)": againKey("ctrl-alt-tab"), #todo make outdent shortcut
        # various
        "comment": againKey("cmd-/"),
        "(match) brace": againKey("cmd-shift-\\"),
        "(ace | care)": Key("alt-;"),
        "((mack | match) (next | neck) | (next | neck) (match | result))": [Key("f4"), set_again("f4", "shift-f4")],
        "((mack | match) preev | (preev) (match | result))": [Key("shift-f4"), set_again("shift-f4", "f4")],
        "problem [(neck | next)]": [Key("f2"), set_again("f2", "shift-f2")],
        "problem (preev | back)": [Key("shift-f2"), set_again("shift-f2", "f2")],
        "top": Key("alt-t"),
        "middle": Key("alt-m"),
        "(mark | remember)": Key("alt-'"),
        "((next | neck) mark | swish)": [againKey("alt-/"), delay(0.1), Key('n enter')],
        "((preev) mark | swoop)": [againKey("alt-/"), delay(0.1), Key('p enter')],
        "(hate | go mark | tisk) [<dgndictation>]": [againKey("alt-/"), text],
        "(action) [<dgndictation>++] [yes]": [againKey(ACTION_POPUP_KEY), text, press_if("enter", "yes$")],
        "search all [<dgndictation>++] [yes]": [againKey("cmd-shift-f"), text, press_if("enter", "yes$")],
        "(complete | drop) [yes]": [Key("ctrl-space"), delay(0.3), press_if("enter", "yes$")],
        
        #vim attempts
        # select/change inside/around <word>
        "{VSCode.vim_action}+ {VSCode.vim_move}+ [<dgndictation>++]": make_vim,
        "{VSCode.vim_action}+ {n.all}+ {basic_keys.alphabet}+": make_vim_simple,
        # "change inside [<dgndictation>]": [Key('escape c i'), text, set_again('escape .')],
        # "change around [<dgndictation>]": [Key('escape c a'), text, set_again('escape .')],
        # "delete inside [<dgndictation>]": [Key('escape d i'), text, set_again('escape .')],
        # "delete around [<dgndictation>]": [Key('escape d a'), text, set_again('escape .')],
        # "select inside [<dgndictation>]": [Key('escape v i'), text],
        # "select around [<dgndictation>]": [Key('escape v a'), text],
        "comment (indent | indentation)": [Key('escape g c i i')],
        "comment parent [(indent | indentation)]": [Key('escape g c a i')],
        "moment": Key("ctrl-o"),
        "star": ['*', set_again('n', 'N')],
        "pound": ['#', set_again('n', 'N')],
        "(greps) [<dgndictation>+] [yes]": [Key('escape /'), text, press_if("enter", "yes$"), set_again('n', 'N')],
        "sup [<dgndictation>+] [yes]": [Key('escape ?'), text, press_if("enter", "yes$"), set_again('n', 'N')],
        "float [<dgndictation>]": [Key('escape f'), text, set_again(';', ',')],
        "(unfloat | backflow | back float) [<dgndictation>]": [Key('escape F'), text, set_again(';', ',')],
        "sneak [<dgndictation>l]": [Key('escape s'), text, set_again(';', ',')],
        "(unsneak | back sneak) [<dgndictation>]": [Key('escape S'), text, set_again(';', ',')],
        "toggle case": "tilde",
        "to end": Key("escape $"),
        "to start": Key("escape ^"),
        "to top": Key("escape g g"),
        "to bottom": Key("escape G"),
        "open": Key("esc o"),
        "big open": Key("esc O"),
        # editing
        "(assign)": " = ",
        "call": "(",
    }

)