
# from https://github.com/JonathanNickerson/talon_voice_user_scripts
# jsc added smileys

from talon.voice import Context, Key

ctx = Context('slack', bundle='com.tinyspeck.slackmacgap')

keymap = {
    '(channel | open)': Key('cmd-k'),
	'next unread': Key('alt-shift-up'),
	'channel up': Key('alt-up'),
    'channel down': Key('alt-down'),
    '(highlight command | insert command)': ['``', Key('left')],
    '(highlight code | insert code)': ['``````', Key('left left left')],

	# jsc: added smileys
    'thumbs up': ':+1:',
    'smiley': ':slightly_smiling_face:',
    'laugh out loud': ':joy:',
}

ctx.keymap(keymap)
