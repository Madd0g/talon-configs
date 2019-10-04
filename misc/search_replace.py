from talon.voice import Context, Key
from ..utils import text
from ..misc.repeat import set_again

ctx = Context("search_replace")

keymap = {
    # "(search | marco) [<dgndictation>] [over]": [Key("cmd-f"), text, Key("enter")],
    "(search | marco) [<dgndictation>+] [over]": [Key("cmd-f"), text, set_again('cmd-g', 'cmd-shift-g')],
    # "marneck": Key("cmd-g"),
    # "marpreev": Key("cmd-shift-g"),
    "marthis": [Key("alt-right"), Key("shift-alt-left"), Key("cmd-f"), Key("enter"), set_again('cmd-g', 'cmd-shift-g')],
    # "(find selected text | find selection | sell find)": Key("cmd-e cmd-f enter"),
    # "set selection [text]": Key("cmd-e"),
    # "set replacement [text]": Key("cmd-shift-e"),
    "([ (search | find) ] [and] replace (selected text | selection) | sell find ace)": Key(
        "cmd-e cmd-alt-f"
    ),
    "([ (search | find) ] [and] replace '[text] | find ace)": Key("cmd-alt-f"),
}

ctx.keymap(keymap)
