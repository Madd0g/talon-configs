# https://github.com/nsaphra/talon_user/blob/master/clipboard.py

# An indexed clipboard.
# If a keyword is included it will save as a clipping under that keyword,
# otherwise behaves as normal copy and paste.
from talon.voice import Key, press, Str, Context
from talon import clip, cron

from ..utils import parse_words, insert, tell_hammerspoon_osa, seti
from ..show_choices import show_choices

ctx = Context('clipboard')

def copy_selection(m):
    if len(m._words) > 1:
        with clip.capture() as sel:
            press('cmd-c')
        key = ' '.join(parse_words(m)).lower()
        value = sel.get()
        # print('saving as', key) # is it taking the first word as well???
        keymap['paste %s' % key] = value
        keymap['free %s' % key] = seti(value)
        ctx.keymap(keymap)
        ctx.reload()
        tell_hammerspoon_osa(f"showAlert('copied to {key}')")

def show_clips(m):
    global ctx
    global keymap
    prefix = 'paste '
    def pick_choice(s):
        # print('inserting from', prefix + s, keymap[prefix + s])
        cron.after("0s", lambda: insert(keymap[prefix + s]))
        
    clips = []
    for trigger in ctx.triggers.keys():
        if trigger.startswith(prefix):
            clips.append(f"{trigger[len(prefix):]}")
    # print(clips)
    if len(clips) > 0:
        # TODO:: max length and take only the (first line | flattened X chars) of the paste!
        values = list(map(lambda s: f"<pre>{keymap[prefix + s]}</pre>", clips))
        show_choices(values, 'clipboard', lambda clip: pick_choice(clip), clips)
    else:
        tell_hammerspoon_osa(f"showAlert('no clips')")
        

keymap = {
    # 'paste': Key('cmd-v'),
    'copy <dgndictation>++': copy_selection,
    '(go | show) clips': show_clips,
}

ctx.keymap(keymap)