
from talon.voice import Key, Context
from ..utils import parse_words_as_integer, repeat_function, optional_numerals, text

ctx = Context("iterm", bundle="com.googlecode.iterm2")

keymap = {
    # "broadcaster": Key("cmd-alt-i"),
    # "password": Key("cmd-alt-f"),
    # Pane creation and navigation
    "full view": Key("cmd-shift-enter"),
    "split horizontal": Key("cmd-shift-d"),
    "split vertical": Key("cmd-d"),
    "pane next": Key("cmd-]"),
    "pane last": Key("cmd-["),
    "pane up": Key("cmd-alt-up"),
    "pane down": Key("cmd-alt-down"),
    "pane left": Key("cmd-alt-left"),
    "pane right": Key("cmd-alt-right"),
    "(switch | find) [<dgndictation>]": [Key("cmd-shift-o"), text],
    "(arnie | start)": "yarn start",
    "run h top": ["htop", Key('enter')],
    "(abort)": Key('ctrl-c'),
    "(clear)": Key('cmd-k'),
    "(fuzzy | history) [<dgndictation>]": [Key('ctrl-r'), text]
}

ctx.keymap(keymap)
