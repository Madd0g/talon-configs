# originally from https://github.com/JonathanNickerson/talon_voice_user_scripts
# and https://github.com/pimentel/talon_user/blob/master/repeat.py
# and https://github.com/dwiel/talon_community/blob/f72dabd505fed9a3a9fe304668412bc609b2094f/misc/repeat.py
from talon.voice import Context, Rep, RepPhrase, talon, Key, press
from .. import utils

ctx = Context("repeater")

# ordinals = {}

# def ordinal(n):
#     """
#     Convert an integer into its ordinal representation::
#         ordinal(0)   => '0th'
#         ordinal(3)   => '3rd'
#         ordinal(122) => '122nd'
#         ordinal(213) => '213th'
#     """
#     n = int(n)
#     suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
#     if 11 <= (n % 100) <= 13:
#         suffix = "th"
#     return str(n) + suffix


# for n in range(2, 100):
#     ordinals[ordinal(n)] = n - 1

# ctx.set_list("ordinals", ordinals.keys())


# def repeat_ordinal(m):
#     o = m["repeater.ordinals"][0]
#     repeater = Rep(int(ordinals[o]))
#     repeater.ctx = talon
#     return repeater(None)

def repeat(m):
    # TODO: This could be made more intelligent:
    #         * Apply a timeout after which the command will not repeat previous actions
    #         * Prevent stacking of repetitions upon previous repetitions
    starts_with_wink = m._words[0] == 'wink'
    if starts_with_wink and len(m._words) == 1:
        repeat_count = 1
    else:
        repeat_count = utils.extract_num_from_m(m)

    if repeat_count is not None:
        # for integrated repeats, need to subtract the first execution
        # "enter five times" will execute enter once and only then repeat, so need to subtract
        if not starts_with_wink and repeat_count >= 2:
            repeat_count -= 1
        
        repeater = Rep(repeat_count)
        repeater.ctx = talon
        return repeater(None)


glob_again = None
glob_back = None
again_phrase = None
again_history = []

def get_repeat_num(m, def_value=1):
    repeat_val = utils.extract_num_from_m(m, 1)
    return def_value if repeat_val == None else repeat_val

# tell_hammerspoon_osa(f"showQuickMessage('')")
# tell_hammerspoon_osa(f"showAlert('')")
def again_action(m):
    global glob_again
    if glob_again != None:
        repeat_again = get_repeat_num(m)
        key_msg = utils.format_keys_unicode(glob_again)
        # utils.tell_hammerspoon_osa(f"showBottomLeftMessage('{key_msg}')")
        for _ in range(repeat_again):
            Key(glob_again)(m)

def back_action(m):
    global glob_back
    if glob_back != None:
        repeat_back = get_repeat_num(m)
        key_msg = utils.format_keys_unicode(glob_back)
        # utils.tell_hammerspoon_osa(f"showBottomLeftMessage('{key_msg}')")
        for _ in range(repeat_back):
            Key(glob_back)(m)

def find_in_agains(phrase):
    global again_history
    for index, item in enumerate(again_history):
        if item[2] == phrase:
            return index, item
    return None, None

def remember_again(again, back, phrase):
    global again_history
    exist_index, exist_item = find_in_agains(phrase)
    if exist_item != None:
        again_history.pop(exist_index)
    again_history.append((again, back, phrase))
    again_history = again_history[-5:]

def get_again_history():
    global again_history
    return again_history
    
    
def set_again(again=None, back=None):
    def set_inner(m):
        global glob_again, glob_back, again_phrase
        glob_again = again
        glob_back = back
        
        again_phrase = utils.format_phrase_with_dictations(m)
        remember_again(glob_again, glob_back, again_phrase)
        # print(again_phrase)

    return set_inner

def againKey(key):
    def _eKey(m):
        global glob_again, glob_back, again_phrase
        glob_again = key
        # if you want back, use set_again
        glob_back = None
        
        # not sure which is better
        # again_phrase = None
        again_phrase = utils.format_phrase_with_dictations(m, True)
        
        Key(key)(m)

    return _eKey

def get_agains():
    global glob_again, glob_back, again_phrase
    return (glob_again, glob_back, again_phrase)

def flip_agains(m):
    global glob_again, glob_back, again_phrase
    flip_label = " - flipped"
    temp_again = glob_again
    glob_again = glob_back
    glob_back = temp_again
    if again_phrase.endswith(flip_label):
        again_phrase = again_phrase[0:-len(flip_label)]
    else:
        again_phrase = again_phrase + flip_label

ctx.keymap(
    {
        # ordinals from 2shea
        # 2nd / 4th / 11th after any command
        # "{repeater.ordinals}": repeat_ordinal,
        
        utils.numerals + '(times | ok)': repeat,
        "(repeat | wink) [" + utils.numerals + ']': repeat,
        
        "(again | shizzle | yarp ) [" + utils.numerals + ']': again_action,
        "(back | fizzle) [" + utils.numerals + ']': back_action,
        # again phrase
        "flip again[s]": flip_agains,
    }
)

