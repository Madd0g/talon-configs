from talon.engine import engine
from talon.voice import Context, Str, press
from talon import applescript, ctrl
from .misc.speech_toggle import set_voice_type, VoiceType
from .utils import delay

context = Context("dragon")

def open_dragon_menubar():
    old = ctrl.mouse_pos()
    x = applescript.run("""
    tell application "System Events" to tell process "Dragon" to tell (menu bar item 1 of menu bar 2)
        set AppleScript's text item delimiters to ", "
        position as string
    end tell
    """)
    x, y = map(int, x.split(", "))
    ctrl.mouse(x+5, y+5)
    ctrl.mouse_click()
    ctrl.mouse(*old)

def open_dragonpad():
    open_dragon_menubar()
    applescript.run("""
        tell application "System Events" to tell process "Dragon" to tell (menu bar item 1 of menu bar 2)
            click menu item "Help" of menu 1
            click menu item "DragonPad" of menu of menu item "Help" of menu 1
        end tell
    """)

# def toggle_status_win(val):
#     open_dragon_menubar()
#     applescript.run(f"""
#     tell application "System Events" to tell process "Dragon" to tell (menu bar item 1 of menu bar 2)
#         click (menu item where its name ends with "Status Window") of menu 1
#     end tell
#     """)

    
def set_status_win(val):
    open_dragon_menubar()
    command = "Show Status Window" if val else "Hide Status Window"
    applescript.run(f"""
    tell application "System Events" to tell process "Dragon" to tell (menu bar item 1 of menu bar 2)
        click menu item "{command}" of menu 1
    end tell
    """)

context.keymap(
    {
        "hide status": lambda m: set_status_win(False),
        "show status": lambda m: set_status_win(True),
        "dragon pad": lambda m: open_dragonpad(),
        # "toggle status": lambda m: toggle_status_win(),
    }
)
context.load()