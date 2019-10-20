
"""
macros are not savable, but they are semantic in that functions are recorded,
not keypresses. This means that macros can interact with your computer state
such as by looking at what is in the clipboard, are referencing nearby text.
"""

from talon.voice import Context, talon, Key, Str, press
from talon.engine import engine

from .utils import parse_words_as_integer, optional_numerals, format_phrase_with_dictations

macro = []
last_actions = None
macro_recording = False


def macro_record(j):
    global macro
    global last_actions
    global macro_recording

    if macro_recording:
        if j["cmd"] == "p.end" and j["grammar"] == "talon":
            new = talon.last_actions
            macro.extend(new)
            last_actions = new


def macro_start(m):
    global macro
    global macro_recording

    macro_recording = True
    macro = []


def macro_stop(m):
    global macro
    global macro_recording

    if macro_recording:
        macro = macro[1:]
        macro_recording = False


def macro_play(m):
    global macro

    macro_stop(None)

    override_num = parse_words_as_integer(m._words)
        
    for item in macro:
        for action, rule in item:
            if override_num != None and 'basic_keys_digits__' in str(rule):
                for char in str(override_num):
                    press(char)
            else:
                action(rule) or (action, rule)


def macro_print(m):
    global macro

    macro_stop(None)

    actions = []
    for item in macro:
        for action, rule in item:
            if isinstance(action, Key):
                actions.append('press("{}")'.format(action.data))
            elif isinstance(action, Str):
                actions.append('Str("{}")(None)'.format(action.data))
            elif '__basic_keys' in str(rule):
                actions.append('press_keys("{}")(None)'.format(format_phrase_with_dictations(rule._words)))
            else:
                # TODO: other conditions
                print(action)
                actions.append(str(action))

    for action in actions:
        Str(action)(None)
        press("enter")


engine.register("post:phrase", macro_record)

ctx = Context("macro")
ctx.keymap(
    {
        "macro (start | record)": macro_start,
        "macro stop": macro_stop,
        "macro play" + optional_numerals: macro_play,
        "macro print": macro_print,
    }
)
