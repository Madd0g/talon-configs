from talon import ui
from talon.voice import Context, press

ctx = Context('globals')

def func(m):
    bundle = ui.active_app().bundle
    if bundle == "com.microsoft.VSCode":
        press('cmd-ctrl-alt-z')
    elif bundle == "com.googlecode.iterm2":
        press('cmd-shift-enter')
    elif bundle == "com.vivaldi.Vivaldi":
        press('f11') #?
    else:
        pass

ctx.keymap({
    'maxi': func,
})