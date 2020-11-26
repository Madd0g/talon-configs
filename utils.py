import collections
import json
import os
import re
import string
from time import sleep, time
import threading
from urllib.parse import urlencode

from talon import clip, resource, applescript, ui
from talon.voice import Context, Str, press, Key
from talon.api import ffi

from . import vocab
from .bundle_groups import FILETYPE_SENSITIVE_BUNDLES, TERMINAL_BUNDLES

INCLUDE_TEENS_IN_NUMERALS = True
INCLUDE_TENS_IN_NUMERALS = False

# mapping = json.load(open(os.path.join(os.path.dirname(__file__), "replace_words.json")))
# doctor(index)
mapping = json.load(resource.open("replace_words.json"))
mapping.update({k.lower(): v for k, v in vocab.vocab_alternate.items()})
mappings = collections.defaultdict(dict)
for k, v in mapping.items():
    mappings[len(k.split(" "))][k] = v

punctuation = set(".,-!?/")

def press_if(key, condition):
    def set_inner(m):
        stringified = format_phrase_with_dictations(m)
        is_match = re.search(condition, stringified) != None
        # print('matched', is_match, stringified)
        if is_match:
            Key(key)(m)
    return set_inner

def local_filename(file, name):
    return os.path.join(os.path.dirname(os.path.realpath(file)), name)

def parse_word(word, force_lowercase=True):
    if force_lowercase:
        word = word.lower()
    word = mapping.get(word, word)

    return word


def replace_words(words, mapping, count):
    if len(words) < count:
        return words

    # print(words, mapping, count)

    new_words = []
    i = 0
    while i < len(words) - count + 1:
        phrase = words[i : i + count]
        key = " ".join(phrase)
        if key in mapping:
            new_words.append(mapping[key])
            i = i + count
        else:
            new_words.append(phrase[0])
            i = i + 1

    new_words.extend(words[i:])
    return new_words


def remove_dragon_junk(word):
    if word == ".\\point\\point":
        return "point"
    else:
        return str(word).lstrip("\\").split("\\", 1)[0].replace("-", " ").strip()


def remove_appostrophe_s(words):
    if "'s" in words:
        new_words = []
        for i, word in enumerate(words):
            if word == "'s":
                new_words[-1] += "s"
            else:
                new_words.append(word)
        return new_words
    else:
        return words

def format_phrase_with_dictations(m, stop_at_dictations=False):
    result = ''
    for i, word in enumerate(m._words):
        if isinstance(word, str):
            result += (word + ' ')
        elif word._name == 'dgndictation':
            if stop_at_dictations:
                return result.strip()
            for j, subword in enumerate(word._data):
                result += (subword + ' ')
    return result.strip()

def parse_words(m, natural=False):
    if isinstance(m, list):
        words = m
    elif hasattr(m, "dgndictation"):
        words = m.dgndictation[0]
    else:
        return []

    # split compound words like "pro forma" into two words.
    words = list(map(remove_dragon_junk, words))
    words = remove_appostrophe_s(words)
    words = sum([word.split(" ") for word in words], [])
    if not natural:
        words = [word.lower() for word in words]

    # replace words and all orders to make sure the replacement is more complete ... a more principled approach here would be nice
    words = replace_words(words, mappings[4], 4)
    words = replace_words(words, mappings[3], 3)
    words = replace_words(words, mappings[2], 2)
    words = replace_words(words, mappings[1], 1)
    # words = list(map(lambda current_word: parse_word(current_word, not natural), words))
    words = replace_words(words, mappings[2], 2)
    words = replace_words(words, mappings[3], 3)
    words = replace_words(words, mappings[4], 4)
    words = sum([word.split(" ") for word in words], [])

    return words

def join_words(words, sep=" "):
    out = ""
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation and out[-1] not in ("/-"):
            out += sep
        out += str(word)
    return out

last_insert = ''
def insert(s):
    global last_insert

    last_insert = s
    
    bundle = ui.active_app().bundle
    if bundle == "com.microsoft.VSCode":
        clip.set(s)
        press('cmd-v')
    else:
        Str(s)(None)

    
    

def select_last_insert(_):
    for _ in range(len(last_insert)):
        press("left")
    for _ in range(len(last_insert)):
        press("shift-right")


def i(s):
    return lambda _: insert(s)

def seti(s):
    return lambda _: insert(s)

def string_capture(m):
    return join_words(parse_words(m)).lower()


def text(m):
    insert(string_capture(m))


def snake_text(m):
    insert(join_words(parse_words(m), sep="_").lower())


def spoken_text(m):
    insert(join_words(parse_words(m, True)))


def sentence_text(m):
    raw_sentence = join_words(parse_words(m, True))
    sentence = raw_sentence[0].upper() + raw_sentence[1:]
    insert(sentence)


def word(m):
    try:
        text = join_words(
            map(lambda w: parse_word(remove_dragon_junk(w)), m.dgnwords[0]._words)
        )
        insert(text.lower())
    except AttributeError:
        pass


def surround(left_surrounder, right_surrounder=None):
    def func(i, word, last):
        if i == 0:
            word = left_surrounder + word
        if last:
            word += right_surrounder or left_surrounder
        return word

    return func


def rot13(i, word, _):
    out = ""
    for c in word.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord("a")) + 13) % 26) + ord("a"))
        out += c
    return out


numeral_map = dict((str(n), n) for n in range(0, 10))
if INCLUDE_TEENS_IN_NUMERALS:
    for n in range(10, 20, 1):
        numeral_map[str(n)] = n
if INCLUDE_TENS_IN_NUMERALS:
    for n in range(20, 101, 10):
        numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    numeral_map[str(n)] = n
numeral_map["oh"] = 0  # synonym for zero
numeral_map["once"] = 1
numeral_map["twice"] = 2
numeral_map["thrice"] = 3

numeral_list = sorted(numeral_map.keys())

ctx = Context("n")
ctx.set_list("all", numeral_list)
numerals = " {n.all}+"
no_prefix_numerals = "{n.all}+"
no_prefix_optional_numerals = "{n.all}*"
optional_numerals = " {n.all}*"


def text_to_number(words):
    tmp = [str(s).lower() for s in words]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        if word not in numeral_list:
            raise Exception("not a number: {}".format(words))

        number = numeral_map[word]
        if number is None:
            continue

        number = int(number)
        if number > 10:
            result = result + number
        else:
            result = result + factor * number
        factor = (10 ** len(str(number))) * factor
    return result


def text_to_range(words, delimiter="until"):
    tmp = [str(s).lower() for s in words]
    split = tmp.index(delimiter)
    start = text_to_number(words[:split])
    end = text_to_number(words[split + 1 :])
    return start, end


number_conversions = {"oh": "0"}  # 'oh' => zero
for i, w in enumerate(
    ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
):
    number_conversions[str(i)] = str(i)
    number_conversions[w] = str(i)
    number_conversions["%s\\number" % (w)] = str(i)


def parse_words_as_integer(words):
    # TODO: Once implemented, use number input value rather than manually
    # parsing number words with this function

    # Ignore any potential non-number words
    number_words = [w for w in words if str(w).strip() in number_conversions]

    # Somehow, no numbers were detected
    if len(number_words) == 0:
        return None

    # Map number words to simple number values
    number_values = list(map(lambda w: number_conversions[w.word], number_words))
    # print(number_values)
    # Filter out initial zero values
    normalized_number_values = []
    non_zero_found = False
    for n in number_values:
        if not non_zero_found and n == "0":
            continue
        non_zero_found = True
        normalized_number_values.append(n)

    # If the entire sequence was zeros, return single zero
    if len(normalized_number_values) == 0:
        normalized_number_values = ["0"]

    # Create merged number string and convert to int
    return int("".join(normalized_number_values))


def alternatives(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")+"


def select_single(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")"


def optional(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")*"


def preserve_clipboard(fn):
    def wrapped_function(*args, **kwargs):
        old = clip.get()
        ret = fn(*args, **kwargs)
        sleep(0.1)
        clip.set(old)
        return ret

    return wrapped_function


# @preserve_clipboard
def paste_text(text):
    with clip.revert():
        clip.set(text)
        # sleep(0.1)
        press("cmd-v")
        sleep(0.1)


# @preserve_clipboard
# def copy_selected():
#     press("cmd-c")
#     sleep(0.25)
#     return clip.get()


def copy_selected(default=None):
    try:
        with clip.capture() as s:
            press("cmd-c")
        return s.get()
    except clip.NoChange:
        return default

def format_keys(keys=''):
    if keys == None:
        return None
        
    keys = keys.replace('cmd-', '&#8984;')
    keys = keys.replace('alt-', '&#8997;')
    keys = keys.replace('option-', '&#8997;')
    keys = keys.replace('ctrl-', '&#8963;')
    keys = keys.replace('shift-', '&#8679;')
    keys = keys.replace('delete', '&#8998;')
    keys = keys.replace('backspace', '&#9003;')
    keys = keys.replace('escape', '&#9099;')
    keys = keys.replace('esc', '&#9099;')
    keys = keys.replace('tab', '&#8677;')
    keys = keys.replace('space', '&#9251;')
    keys = keys.replace('enter', '&#8617;')
    
    keys = keys.replace('pageup', '&#8670;')
    keys = keys.replace('pagedown', '&#8671;')
    # arrows
    keys = keys.replace('right', '&#8594;')
    keys = keys.replace('left', '&#8592;')
    keys = keys.replace('up', '&#8593;')
    keys = keys.replace('down', '&#8595;')
    return keys

def format_keys_unicode(keys=''):
    keys = '' if keys == None else keys
    keys = keys.replace('cmd-', '⌘')
    keys = keys.replace('ctrl-', '⌃')
    keys = keys.replace('alt-', '⌥')
    keys = keys.replace('option-', '⌥')
    keys = keys.replace('shift-', '⇧')
    keys = keys.replace('delete', '⌦')
    keys = keys.replace('backspace', '⌫')
    keys = keys.replace('escape', '⎋')
    keys = keys.replace('esc', '⎋')
    keys = keys.replace('tab', '⇥')
    keys = keys.replace('space', '␣')
    keys = keys.replace('enter', '↩')
    
    keys = keys.replace('pageup', '⇞')
    keys = keys.replace('pagedown', '⇟')
    # arrows
    keys = keys.replace('right', '→')
    keys = keys.replace('left', '←')
    keys = keys.replace('up', '↑')
    keys = keys.replace('down', '↓')
    return keys


# The. following function is used to be able to repeat commands by following it by one or several numbers, e.g.:
# 'delete' + optional_numerals: repeat_function(1, 'delete'),
def repeat_function(numberOfWordsBeforeNumber, keyCode, delay=0):
    def repeater(m):
        if numberOfWordsBeforeNumber > 0:
            line_number = parse_words_as_integer(m._words[numberOfWordsBeforeNumber:])
        else:
            line_number = parse_words_as_integer(m._words[:numberOfWordsBeforeNumber])

        if line_number is None:
            line_number = 1

        for i in range(0, line_number):
            sleep(delay)
            press(keyCode)

    return repeater


def delay(amount=0.1):
    return lambda _: sleep(amount)


def is_in_bundles(bundles):
    def _is_in_bundles(app, win):
        return any(b in app.bundle for b in bundles)

    return _is_in_bundles


def is_filetype(extensions=(), default=False):
    def matcher(app, win):
        if is_in_bundles(FILETYPE_SENSITIVE_BUNDLES)(app, win):
            if any(ext in win.title for ext in extensions):
                return True
            else:
                return False
        return default

    return matcher

luaDict = {
    'true': True,
    'false': False,
    'nil': None,
}

def tell_alfred_flow(workflow, trigger, arg=None):
    argument = f' with argument "{arg}"' if arg != None else ""
        
    script = f'''
    tell application "Alfred 4" to run trigger "{trigger}" in workflow "{workflow}"{argument}'''
    # print(script)
    try:
        ret = applescript.run(script)
    except applescript.ApplescriptErr:
        print('alfred osa error:', script)
        raise
    if ret:
        if isinstance(ret, str) and luaDict[ret]:
            return luaDict[ret]
        
        print('alfred osa returned: ', ret)
        result = ffi.string(ret).decode('utf8')
        # print('osa said: ', result)
        return result
    
def tell_hammerspoon_cli(code):
    command = f'''
    /usr/local/bin/hs -q -c "{code}"'''
    os.system(command)
    
def tell_hammerspoon_osa(code):
    script = f'''
    tell application "Hammerspoon"
        return execute lua code "{code}"
    end tell'''
    # print(script)
    try:
        ret = applescript.run(script)
    except applescript.ApplescriptErr:
        print('osa error:', script)
        raise
    if ret:
        if isinstance(ret, str) and luaDict[ret]:
            return luaDict[ret]
        
        print(script)
        print('osa returned: ', ret)
        result = ffi.string(ret).decode('utf8')
        # print('osa said: ', result)
        return result

def extract_num_from_m(m, default=ValueError):
    # loop identifies numbers in any message
    number_words = [w for w in m._words if w in numeral_list]
    if len(number_words) == 0:
        if default is ValueError:
            raise ValueError("No number found")
        else:
            return default
    return text_to_number(number_words)


# Handle ( x | y ) syntax in dicts used to create keymaps indirectly.
# Do not be deceived, this is not real Talon syntax and [] wont work
def normalise_keys(dict):
    normalised_dict = {}
    for k, v in dict.items():
        for cmd in k.strip("() ").split("|"):
            normalised_dict[cmd.strip()] = v
    return normalised_dict

def throttle(s):
    """Decorator ensures function that can only be called once every `s` seconds.
    """
    def decorate(f):
        t = None

        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time()
            if t is None or t_ - t >= s:
                result = f(*args, **kwargs)
                t = time()
                return result
        return wrapped
    return decorate

def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """

    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                debounced._timer = None
                debounced._last_call = time()
                return fn(*args, **kwargs)

            time_since_last_call = time() - debounced._last_call
            if time_since_last_call >= wait:
                return call_it()

            if debounced._timer is None:
                debounced._timer = threading.Timer(wait - time_since_last_call, call_it)
                debounced._timer.start()

        debounced._timer = None
        debounced._last_call = 0

        return debounced

    return decorator