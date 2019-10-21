
"""
macros are not savable, but they are semantic in that functions are recorded,
not keypresses. This means that macros can interact with your computer state
such as by looking at what is in the clipboard, are referencing nearby text.
"""

import time

from talon.voice import Context, talon, Key, Str, press
from talon.engine import engine

from .utils import parse_words_as_integer, optional_numerals, format_phrase_with_dictations

macro = []
last_actions = None
macro_recording = False
last_usage = None
RECORD_PHRASE = 'macro start'
STOP_PHRASE = 'macro stop'

def macro_record(j):
    global macro
    global last_actions
    global macro_recording
    global last_usage
    
    if macro_recording:
        if j["cmd"] == "p.end" and j["grammar"] == "talon":
            new = talon.last_actions
            macro.extend(new)
            last_actions = new
            last_usage = time.time()

def macro_start(m):
    global macro
    global macro_recording

    macro_recording = True
    macro = []

def is_recording():
    global macro_recording
    return macro_recording

def macro_record_phrase():
    global RECORD_PHRASE
    return RECORD_PHRASE

def macro_stop_phrase():
    global STOP_PHRASE
    return STOP_PHRASE
    
def display_macro():
    if last_usage == None:
        return False
    now = time.time()
    return now - last_usage < 120
    

def macro_stop(m):
    global macro
    global macro_recording
    global last_usage
    last_usage = time.time()

    if macro_recording:
        macro = macro[1:]
        macro_recording = False


def macro_play(m):
    global macro
    global last_usage
    last_usage = time.time()
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
    global last_usage
    last_usage = time.time()
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
        RECORD_PHRASE: macro_start,
        STOP_PHRASE: macro_stop,
        "macro play": macro_play,
        "(replay)" + optional_numerals: macro_play,
        "macro print": macro_print,
    }
)
