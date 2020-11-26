from talon.voice import Context, press
from talon import ui
import time
import os

from ..utils import join_words, tell_hammerspoon_cli, text
from .speech_toggle import set_voice_type, VoiceType
from talon.voice import Context, Key, Str, press

running = {}
launch = {}


def lookup_app(m=None, name=None):
    if isinstance(m, str):
        name = m
    elif name is None:
        name = str(m["switcher.running"][0])

    # full = running.get(name)
    full = hardcoded_application_names.get(name)
    if not full:
        return
    if full.startswith('hs:') or full.startswith('key:'):
        return full
    for app in ui.apps():
        if app.name == full:
            return app

def hammer_switch_app(alias, say_name=None):
    script = f"activateAppByAlias('{alias}')"
    # if say_name != None:
        # set_voice_type(VoiceType.SLEEPING, True)
        # script += f"speakTextFast('{say_name}', true)"
        
    tell_hammerspoon_cli(script)
    
def switch_app(m=None, name=None):
    app = lookup_app(m=m, name=name)
    if isinstance(app, str) and app.startswith("hs:"):
        app_name = app.replace("hs:", "")
        say_name = join_words(m._words[1:])
        hammer_switch_app(app_name, say_name)
    elif isinstance(app, str) and app.startswith("key:"):
        send_key = app.replace("key:", "")
        press(send_key)
    else:
        app.focus()
        # print(dir(app))
        # TODO: replace sleep with a check to see when it is in foreground
        time.sleep(0.25)

def launch_app(m=None, name=None):
    if m:
        name = str(m["switcher.launch"][0])
    elif not name:
        raise ValueError("must provide name or m")

    path = launch.get(name)
    if path:
        ui.launch(path=path)


ctx = Context("switcher")
ctx.keymap(
    {
        "(focus | fox | focks | win) {switcher.running}": switch_app,
        "launch {switcher.launch}": launch_app,
        # custom switchers here
        # "madam": lambda x: switch_app(x, "Atom"),
        "(fox app) [<dgndictation>+]": [Key("ctrl-alt-shift-cmd-f8"), text],
        # "system preferences": lambda x: switch_app(x, "System Preferences"),
    }
)

hardcoded_application_names = {
    # through hammerspoon
    "term": "hs:iterm",
    "browser": "hs:browser",
    "web": "hs:browser",
    "lack": "hs:slack",
    "auto": "key:cmd-alt-ctrl-3",
    # "smart": "key:cmd-alt-ctrl-3",
    # "mart": "key:cmd-alt-ctrl-3",
    "cool": "key:cmd-alt-ctrl-3",
    "play": "key:cmd-alt-ctrl-shift-f9",
    "else": "key:cmd-alt-ctrl-shift-f8",
    "hunt": "key:cmd-alt-ctrl-shift-f8",
    "music": "hs:spotify",
    "password": "hs:keepass",
    "fire fox": "hs:firefox",
    "fire": "hs:firefox",
    # "chrome": "hs:browser",
    "chuck": "hs:whatsapp",
    "chat": "hs:whatsapp",
    "quicktime": "hs:quicktime",
    "notes": "hs:boostnote",
    "code": "hs:code",
    "finder": "hs:finder",
}

def update_lists():
    global running
    global launch
    new = {}
    for app in ui.apps():
        if app.background and not app.windows():
            continue
        words = app.name.split(" ")
        for word in words:
            if word and word not in new:
                new[word] = app.name
        new[app.name] = app.name
    running = new
    running.update(hardcoded_application_names)
    ctx.set_list("running", running.keys())

    new = {}
    for base in "/Applications", "/Applications/Utilities":
        for name in os.listdir(base):
            path = os.path.join(base, name)
            name = name.rsplit(".", 1)[0]
            new[name] = path
            words = name.split(" ")
            for word in words:
                if word and word not in new:
                    if len(name) > 6 and len(word) < 3:
                        continue
                    new[word] = path
    launch = new
    ctx.set_list("launch", launch.keys())


def ui_event(event, arg):
    if event in ("app_activate", "app_launch", "app_close", "win_open", "win_close"):
        # print(event, arg)
        if event in ("win_open", "win_closed"):
            if arg.app.name == "Amethyst":
                return
        update_lists()


# ui.register("", ui_event)
# update_lists()
ctx.set_list("running", hardcoded_application_names)
