
# from https://github.com/JonathanNickerson/talon_voice_user_scripts
# jsc added smileys

from talon.voice import Context, Key
from .. import utils

ctx = Context('slack', bundle='com.tinyspeck.slackmacgap')

keymap = {
    '(channel)': Key('cmd-k'),
    "channel <dgndictation>": [Key("cmd-k"), utils.text],
    "direct messages": Key("cmd-shift-k"),
    "(my stuff | activity)": Key("cmd-shift-m"),
	'next unread': Key('alt-shift-up'),
	'channel up': Key('alt-up'),
    'channel down': Key('alt-down'),
    "(unread threads | new threads | threads)": Key("cmd-shift-t"),
    '(highlight command | insert command)': ['``', Key('left')],
    '(highlight code | insert code)': ['``````', Key('left left left')],

    "((open | collapse) right pane | toggle sidebar)": Key("cmd-."),
    "(go back)": Key('cmd-['),
    "(go forward)": Key('cmd-]'),
    "upload": Key("cmd-u"),
    "snippet": Key("cmd-shift-enter"),

    "(bullet | bulleted) list": Key("cmd-shift-8"),
    "(number | numbered) list": Key("cmd-shift-7"),
    "(quotes | quotation)": Key("cmd-shift->"),
    "bold": Key("cmd-b"),
    "(italic | italicize)": Key("cmd-i"),
    "(strike | strikethrough)": Key("cmd-shift-x"),
    "(react | reaction)": Key("cmd-shift-\\"),
	# jsc: added smileys
    'thumbs up': ':+1:',
    'smiley': ':slightly_smiling_face:',
    'laugh out loud': ':joy:',
}

ctx.keymap(keymap)
