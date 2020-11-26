import time
import glob
import os

from .. import utils
from .. import config
from .web import browser
from ..misc import switcher
from ..misc.repeat import set_again

from talon import ui, ctrl
from talon.voice import Context, Key, Str, press

context = Context("GoogleChrome", bundle="com.google.Chrome")


def most_recently_downloaded_file():
    list_of_files = glob.glob(os.path.expanduser("~/Downloads/*"))
    return max(list_of_files, key=os.path.getctime)


def open_most_recently_downloaded_file(m):
    os.system(f"open {most_recently_downloaded_file()}")


def get_url(win=None):
    if win is None:
        win = ui.active_window()
    return tuple(win.children.find(AXRole="AXTextField")[0].AXValue)[0].AXValue


def set_url(url, win=None):
    if win is None:
        win = ui.active_window()
    focus_address_bar()
    utils.paste_text(url)


def navigate_to_url(url, win=None):
    set_url(url, win)
    press("enter")


def open_focus_devtools(m):
    press("cmd-shift-c")


def show_panel(name):
    open_focus_devtools(None)

    # Open command menu
    press("cmd-shift-p")
    time.sleep(0.2)
    Str("Show %s" % (name))(None)
    time.sleep(0.2)
    press("enter")


def next_panel(m):
    open_focus_devtools(None)
    press("cmd-]")


def last_panel(m):
    open_focus_devtools(None)
    press("cmd-[")


def focus_address_bar(m=None):
    press("cmd-l")
    time.sleep(0.1)


# Return focus from the devtools to the page
def refocus_page(m):
    focus_address_bar(None)
    press(";")
    press("enter")
    # focus_address_bar(None)
    # press("escape")
    # press("escape")
    # # time.sleep(0.1)
    # # This leaves the focus on the page at previous tab focused point, not the beginning of the page
    # press("tab")


def back(m):
    refocus_page(None)
    press("cmd-[")
    # refocus_page(None)


def forward(m):
    refocus_page(None)
    press("cmd-]")
    refocus_page(None)


def link(m):
    refocus_page(None)
    press("f")


def jump_tab(m):
    tab_number = utils.parse_words_as_integer(m._words[1:])
    if tab_number is not None and tab_number > 0 and tab_number < 9:
        press("cmd-%s" % tab_number)


webpages = config.load_config_json("webpages.json")


def get_webpage(m):
    return webpages[" ".join(m["global_browser.webpages"])]


def go_to_webpage(m):
    press("cmd-t")
    navigate_to_url(get_webpage(m))


def get_search(m):
    return searches[" ".join(m["global_browser.searches"])]


searches = config.load_config_json("searches.json")


def new_search_new_tab(m):
    press("cmd-t")
    utils.insert(get_search(m))
    press("tab")
    search_text = utils.join_words(utils.parse_words(m))
    if search_text:
        print(search_text)
        utils.insert(search_text)
        press("enter")


def new_search_existing_tab(m):
    press("cmd-l")
    utils.insert(get_search(m))
    press("tab")
    search_text = utils.join_words(utils.parse_words(m))
    if search_text:
        print(search_text)
        utils.insert(search_text)
        press("enter")


context.keymap(
    {
        "(address bar | focus address | focus url | url | goto address)": focus_address_bar,
        "copy url": Key("escape y y"),
        "clone tab": Key("escape y t"),
        "(go back)": back,
        "(go forward | forward)": forward,
        "reload": Key("cmd-r"),
        "page": Key("escape d"),
        # "page reload": Key("cmd-r"),
        # "reload page": Key("cmd-r"),
        "hard reload": Key("cmd-shift-r"),
        "new tab": Key("cmd-t"),
        # "new tab {global_browser.webpages}": go_to_webpage,
        # "new search {global_browser.searches} [<dgndictation>]": new_search_new_tab,
        # "search {global_browser.searches} [<dgndictation>]": new_search_existing_tab,
        "close tab": [Key("cmd-w"), set_again('cmd-w', "cmd-shift-t")],
        "(reopen | unclose) tab": [Key("cmd-shift-t"), set_again('cmd-shift-t', None)],
        "recently closed": [refocus_page, Key("\\x")],
        "close others": [refocus_page, Key('g x x')],
        "(next tab | goneck)": Key("cmd-shift-]"),
        "((last | previous | preev) tab | gopreev)": Key("cmd-shift-["),
        "tab (1 | 2 | 3 | 4 | 5 | 6 | 7 | 8)": jump_tab,
        "(end | rightmost) tab": Key("cmd-9"),
        "marco": Key("cmd-f"),
        "(marneck)": Key("cmd-g"),
        "(last | prevous)": Key("cmd-shift-g"),
        "toggle dev tools": Key("cmd-alt-i"),
        "edit [current] url": [refocus_page, Key("s U")],
        "edit new url": [refocus_page, Key("s u")],
        "command menu": Key("cmd-shift-p"),
        "next panel": next_panel,
        "next page": [refocus_page, Key('] ]'), set_again('] ]', '[ [')],
        "(preev | previous) page": [refocus_page, Key('[ ['), set_again('[ [', '] ]')],
        # reddit comment
        "collapse next": [Key('enter j'), set_again('enter j', 'k enter')],
        # "thread next": [Key('alt-shift-j'), set_again('alt-shift-j', 'alt-shift-k')],
        # "thread back": [Key('alt-shift-k'), set_again('alt-shift-k', 'alt-shift-j')],
        "thread next": Key('alt-shift-j'),
        "thread back": Key('alt-shift-k'),
        "(comment back | thread ups)": Key('ctrl-z'),
        "read selected": Key('space r'),
        "go hi": Key('alt-t'),
        "expand": Key('alt-3 alt-9'),
        "comments": Key('alt-0'),
        "reddit mode": Key('alt-d'),
        "[go] (top | toop)": Key('alt-t'),
        "(pin tab)": Key('alt-p'),
        "(mute tab)": Key('alt-m'),
        "expand": Key('alt-3 alt-9'),
        "comments": Key('alt-0'),
        "[open | hey] mark [<dgndictation>]": [Key('`'), utils.text],
        "go mark [<dgndictation>]": [refocus_page, Key('o m'), utils.text],
        # "remember <dgndictation>": [Key('m'), (False, lambda i, word, _: word.capitalize())],
        "(last | previous) panel": last_panel,
        "show application [panel]": lambda m: show_panel("Application"),
        "show audit[s] [panel]": lambda m: show_panel("Audits"),
        "show (console|consul) [panel]": lambda m: show_panel("Console"),
        "show element[s] [panel]": lambda m: show_panel("Elements"),
        "show memory [panel]": lambda m: show_panel("Memory"),
        "show network [panel]": lambda m: show_panel("Network"),
        "show performance [panel]": lambda m: show_panel("Performance"),
        "show security [panel]": lambda m: show_panel("Security"),
        "show (source[s] | code) [panel]": lambda m: show_panel("Sources"),
        "(refocus | focus) page": refocus_page,
        "[refocus] dev tools": open_focus_devtools,
        "type": Key("cmd-;"),
        "vim type": [refocus_page, Key("I")],
        "(flesh) [<dgndictation>+] [yes]": [Key("/"), utils.text, utils.press_if("enter", "yes$"), set_again('n', 'N')],
        # visual mode vim
        "float [<dgndictation>]": [refocus_page, Key('f'), utils.text, set_again(';', ',')],
        "(unfloat | backflow) [<dgndictation>]": [refocus_page, Key('F'), utils.text, set_again(';', ',')],
        # Clipboard
        # "cut": Key("cmd-x"),
        # "copy": Key("cmd-c"),
        # "paste": Key("cmd-v"),
        # "paste same style": Key("cmd-alt-shift-v"),
        # TODO: this should probably be specific to the page
        "submit": Key("cmd-enter"),
        "omni next": [Key('ctrl-.'), set_again('ctrl-.', 'ctrl-,')],
        "omni (preev | last)": [Key('ctrl-,'), set_again('ctrl-,'), 'ctrl-.'],
        "omni (remove | delete)": Key('ctrl-d'),
        "omni (open)": Key('ctrl-enter'),
        # custom button search
        "button [<dgndictation>+] [yes]": [
            Key('alt-shift-f7'),
            utils.delay(0.1),
            utils.text,
            utils.press_if("enter", "yes$"),
        ],
        # zotero
        # "zotero": Key("cmd-shift-z"),
        # rearrange tabs: https://chrome.google.com/webstore/detail/rearrange-tabs/ccnnhhnmpoffieppjjkhdakcoejcpbga
        # "move tab left": Key("ctrl-shift-left"),
        # "move tab right": Key("ctrl-shift-right"),
        # "move tab left way": Key("ctrl-shift-down"),
        # vimium
        # "link": link,
        "(last place | bimsko)": [Key('ctrl-6')],
        "very far": browser.send_to_vimium("\\i"),
        "move tab right": browser.send_to_vimium(">>"),
        "move tab new window": browser.send_to_vimium("W"),
        "tab (named | name | by name)": browser.send_to_vimium("T"),
        "tab (named | name | by name) <dgndictation>+": [
            browser.send_to_vimium("T"),
            lambda m: time.sleep(0.3),
            lambda m: utils.paste_text(utils.string_capture(m)),
            lambda m: time.sleep(0.0),
            Key("enter"),
        ],
        "open most recently downloaded file": open_most_recently_downloaded_file,
    }
)


def global_chrome_new_tab(m):
    switcher.switch_app(name="Google Chrome")
    press("cmd-t")


def global_go_to_webpage(m):
    switcher.switch_app(name="Google Chrome")
    go_to_webpage(m)


def global_chrome_close_tab(m):
    current_app = ui.active_window().app
    switcher.switch_app(name="Google Chrome")
    press("cmd-w")
    current_app.focus()
    # app = ui.apps(bundle="com.google.Chrome")[0]
    # ctrl.key_press("w", cmd=True, app=app)


global_ctx = Context("global_browser")
global_ctx.set_list("webpages", webpages.keys())
global_ctx.set_list("searches", searches.keys())
global_ctx.keymap(
    {
        "chrome new tab": global_chrome_new_tab,
        "chrome new [tab] {global_browser.webpages}": global_go_to_webpage,
        "chrome close tab": global_chrome_close_tab,
        "chrome search [<dgndictation>]": [global_chrome_new_tab, utils.text, " "],
        'toggle bookmarks' : Key('cmd-shift-B'),
        "chrome lucky [<dgndictation>]": [
            global_chrome_new_tab,
            "lucky ",
            utils.text,
            " ",
        ],
    }
)
