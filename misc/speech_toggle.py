from talon.voice import Context, ContextGroup, Key
from talon.engine import engine
from talon_plugins import speech
from talon import speechd, cron
from ..utils import tell_hammerspoon_cli

sleep_group = ContextGroup("sleepy")
sleepy = Context("sleepy", group=sleep_group)

from ..misc.dictation import dictation_group

class VoiceType:
    SLEEPING = 1
    TALON = 2
    DRAGON = 3
    DICTATION = 4

voice_type = VoiceType.TALON
last_voice_type = VoiceType.TALON

statuses = {
    VoiceType.TALON: 'talon',
    VoiceType.DRAGON: 'dragon',
    VoiceType.DICTATION: 'dictation',
    VoiceType.SLEEPING: 'sleeping',
}

def show_mode_message():
    global voice_type, last_voice_type
    mode = statuses[voice_type]
    if voice_type == VoiceType.DRAGON or voice_type == VoiceType.DICTATION:
        msg = f'{mode} active'
        icon = '🐲'
    elif voice_type == VoiceType.SLEEPING:
        msg = 'talon sleeping'
        icon = '💤'
    else:
        msg = 'talon mode'
        icon = '🦅'
    # tell_hammerspoon_cli(f"showQuickMessage('{mode} active')")
    tell_hammerspoon_cli(f"showAlert('{icon} {msg}')")

def set_voice_type(type, silent=None):
    global voice_type, last_voice_type
    if voice_type != VoiceType.SLEEPING:
        last_voice_type = voice_type
    voice_type = type

    talon_enabled = type == VoiceType.TALON
    dragon_enabled = type == VoiceType.DRAGON
    dictation_enabled = type == VoiceType.DICTATION

    global speech
    speech.set_enabled(type == VoiceType.TALON or type == VoiceType.DICTATION)

    global dictation_group
    if not dictation_enabled:
        dictation_group.disable()

    global engine
    if dragon_enabled:
        engine.mimic("wake up".split())
    elif last_voice_type == VoiceType.DRAGON:
    # else:
        engine.mimic("go to sleep".split())

    if dictation_enabled:
        # Without postponing this "go to sleep" will be printed
        cron.after("0s", lambda: dictation_group.enable())
        
    if silent == None:
        show_mode_message()

def stop_voice(m):
    set_voice_type(VoiceType.SLEEPING)
    speechd.kill()

sleepy.keymap(
    {
        '(snore | talon sleep)': lambda m: set_voice_type(VoiceType.SLEEPING),
        '(unsnore | talon wake)': lambda m: set_voice_type(last_voice_type),
        "talon mode": lambda m: set_voice_type(VoiceType.TALON),
        "dragon mode": lambda m: set_voice_type(VoiceType.DRAGON),
        "dictation mode": lambda m: set_voice_type(VoiceType.DICTATION),
        # mute the mic itself
        '(global snore | global mute)': Key('cmd-ctrl-alt-shift-s'),
        # fully stop speech engine (keeps noises and other features alive)
        "talon suicide": stop_voice,
    }
)

sleep_group.load()
# set_voice_type(VoiceType.TALON)