
from talon.voice import Key, Context
from ..utils import parse_words_as_integer, repeat_function, optional_numerals, text

ctx = Context("iterm", bundle="com.googlecode.iterm2")

keymap = {
    # "broadcaster": Key("cmd-alt-i"),
    # "password": Key("cmd-alt-f"),
    # Pane creation and navigation
    "split horizontal": Key("cmd-shift-d"),
    "split vertical": Key("cmd-d"),
    "pane next": Key("cmd-]"),
    "pane last": Key("cmd-["),
    "(switch | find) [<dgndictation>]": [Key("cmd-shift-o"), text],
    "(arnie | start)": "yarn start",
    "(abort)": Key('ctrl-c'),
    "(clear)": Key('cmd-k'),
    "fuzzy [<dgndictation>]": [Key('ctrl-r'), text]
}

ctx.keymap(keymap)
