from talon import webview, ui, cron
from talon.engine import engine
from talon.voice import Context
import functools

from .misc.repeat import get_agains, get_again_history
from .utils import format_keys
from .show_choices import show_choices
from .macro import is_recording, display_macro, macro_record_phrase, macro_stop_phrase

hist_len = 3
show_agains = True

template = '''
<style type="text/css">
body {
    width: 400px;
    padding: 0;
    margin: 0;
}
.contents, table, h3 {
    width: 100%;
}
table {
    table-layout: fixed;
}
td {
    overflow-wrap: normal;
    word-wrap: normal;
    text-align: left;
    margin: 0;
    padding: 0;
    padding-left: 5px;
    padding-right: 5px;
}
.text {
    font-weight: normal;
    font-style: italic;
}
#title {
    background-color: rgb(203, 203, 250) !important;
    min-height: 1em;
    padding: 3px 10px;
    opacity: 0.8;
    position: relative;
    display: flex;
    color: black;
    flex: 1;
    max-width: 380px;
    justify-content: space-between;
}
#again {
    border-top: 1px solid black;
    padding: 2px 0;
    background-color: rgb(203, 203, 250) !important;
    opacity: 0.8;
}
#macro {
    border-top: 1px solid black;
    padding: 2px 0;
    background-color: rgba(203, 0, 0, 0.3) !important;
    opacity: 0.8;
}
.number {
    background-color: rgba(0,0,0,0.45);
    border-radius: 6px;
    padding: 1px 2px;
    color: white;
    visibility: hidden;
}
.number.recording {
    background-color: red;
    color: red;
    padding: 3px;
    width: 5px;
    height: 5px;
    display: inline-block;
    border-radius: 50px;
    visibility: visible;
}
</style>

<!--<h3 id="title">History</h3>-->
<table>
{% for phrase, text, number in phrases %}
<tr><td colspan="3" class="phrase">
<span class="number" {% if number > 1 %}style="visibility:visible;"{% endif %}>{{ number }}</span>
{{ phrase }}
</td></tr>
{% endfor %}
{% if agains[0] != None and show_again %}
    <tr id="again">
        <td><span class="number">0</span>{{ agains[0] }}</td>
        <td {% if agains[1] == None %}colspan="2" {%endif%} style="text-align: {% if agains[1] != None %}center{%else%}right{%endif%};"><span style='white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>({{ agains[2] }})</span></td>
        {% if agains[1] != None %}<td style="text-align: right;">{{ agains[1] }}<span class="number">0</span></td>{% endif %}
    </tr>
{% endif %}
{% if show_macro %}
    <tr id="macro">
        <td colspan="3">{% if recording %}<span class="number recording"></span>{%endif%}{% if not recording %}<span class="number">0</span><strong>macro:</strong>{%endif%} {{recorded}}</td>
    </tr>
{% endif %}
</table>
'''

webview = webview.Webview()
webview.render(template, phrases=[('--start--', '', 1)], agains=(None, None, None), show_again=show_agains)
webview.move(ui.main_screen().width - 400, ui.main_screen().height)

class History:
    def __init__(self):
        self.history = []
        self.macro_history = []
        self.timer = cron.after('15s', self.auto_hide)
        self.auto_hidden = False
        engine.register('post:phrase', self.on_phrase_post)
        # engine.register('pre:phrase', self.on_phrase_pre)

    def parse_phrase(self, phrase):
        return ' '.join(word.split('\\')[0] for word in phrase)

    def auto_hide(self):
        self.auto_hidden = True
        # webview.set_element_attribute()
        webview.hide()

    def on_phrase_pre(self, j):
        print(j)
        
    def on_phrase_post(self, j):
        phrase = self.parse_phrase(j.get('phrase', []))
        if phrase in ('history show', 'history hide'):
            return
        cmd = j['cmd']
        if cmd == 'p.end' and phrase:
            if len(self.history) > 0 and self.history[-1][0] == phrase:
                self.history[-1] = (phrase, '', self.history[-1][2] + 1)
            else:
                self.history.append((phrase, '', 1))
                self.history = self.history[-hist_len:]
            if phrase == macro_record_phrase():
                self.macro_history = []
            elif is_recording() and phrase != macro_stop_phrase():
                self.macro_history.append(phrase)
            self.render()
            if self.auto_hidden:
                webview.show()
            if self.timer != None:
                cron.cancel(self.timer)
            self.timer = cron.after('15s', self.auto_hide)
            
    def render(self):
        global show_agains
        agains = get_agains()
        agains = (format_keys(agains[0]), format_keys(agains[1]), agains[2])
        show_macro = is_recording() or display_macro()
        webview.render(template, phrases=self.history, agains=agains, show_again=show_agains, show_macro=show_macro, recording=is_recording(), recorded="␣".join(self.macro_history))
    
history = History()

def toggle_agains(m):
    global show_agains
    show_agains = not show_agains
    history.render()

def pick_again(m):
    history = get_again_history()
    choices = list(map(lambda item: f"{item[2]}", history))
    show_choices(choices, None, lambda phrase: engine.mimic(phrase.split()))
    

ctx = Context('phrase_history')
ctx.keymap({
    'history show': lambda m: webview.show(),
    'history hide': lambda m: webview.hide(),
    "(show | hide | toggle) again[s]": toggle_agains,
    "(pick again | rerun | re run)": pick_again,
})
webview.show()
