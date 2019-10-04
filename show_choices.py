# ripped from homophones.py
from talon import app, clip, cron
from talon.voice import Context, Str, press
from talon.webview import Webview

from .utils import parse_word
import os
pick_context = Context("pick_choice")

webview = Webview()
css_template = """
<style type="text/css">
body {
    padding: 0;
    margin: 0;
    font-size: 150%;
    min-width: 600px;
}

td {
    text-align: left;
    margin: 0;
    padding: 5px 10px;
}

h3 {
    padding: 5px 0px;
}

table {
    counter-reset: rowNumber;
}

table .count {
    counter-increment: rowNumber;
}

.count td:first-child::after {
    content: counter(rowNumber);
    min-with: 1em;
    margin-right: 0.5em;
}

.pick {
    font-weight: normal;
    font-style: italic;
}

.cancel {
    text-align: center;
}

</style>
"""

choices_template = (
    css_template
    + """
<div class="contents">
{% if title %}<h3>{{title}}</h3>{% endif %}
<table>
{% for word in choices %}
<tr class="count"><td class="pick">🔊 pick </td><td>{{ word }}</td></tr>
{% endfor %}
<tr><td colspan="2" class="pick cancel">🔊 cancel</td></tr>
</table>
</div>
"""
)


def close_choices():
    webview.hide()
    pick_context.unload()


def make_selection(m, choices, callback):
    cron.after("0s", close_choices)
    words = m._words
    d = None
    if len(words) == 1:
        d = int(parse_word(words[0]))
    else:
        d = int(parse_word(words[1]))
    
    choice = choices[d - 1]
    callback(choice)

def show_choices(choices, title, callback):
    global pick_context
    if len(choices) < 1:
        print('no choices to show')
        return
    webview.render(choices_template, choices=choices, title=title)
    webview.show()

    keymap = {"(cancel | 0)": lambda x: close_choices()}
    valid_indices = range(len(choices))
    keymap.update(
        {
            "[pick] %s" % (i + 1): lambda m: make_selection(m, choices, callback)
            for i in valid_indices
        }
    )
    pick_context.keymap(keymap)
    pick_context.load()
