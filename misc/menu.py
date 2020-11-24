import appscript
from talon import ctrl, ui
from talon.voice import Context

def get_app():
    return appscript.app('System Events').processes[appscript.its.frontmost == True].get()[0]

def name_and_centers(obj):
    try:
        names = obj.name.get()
        positions = obj.position.get()
        sizes = obj.size.get()
    except Exception:
        return {}
    center = {}
    for name, pos, size in zip(names, positions, sizes):
        if appscript.k.missing_value in (name, pos, size) or not all((name, pos)):
            continue

        center[name] = (pos[0] + 5, pos[1] - 5) # (pos[0] + size[0] / 2, pos[1] + size[1] / 2)
    return center

def get_menu(menu_bar, path):
    menu = cur = menu_bar.menus[path[0]]
    if len(path) > 1:
        cur = cur.menu_items[path[1]]
        menu = cur.menus[1]
    for item in path[2:]:
        cur = cur.menus.menu_items[item]
        menu = cur.menus[1]
    return cur, menu

class MenuWatcher:
    def __init__(self):
        ui.register('app_activate', self.update)
        ui.register('win_focus', lambda win:
                    win == ui.active_window() and self.update(win.app))
        self.path = []

    def update(self, app=None):
        if app is not None and app != ui.active_app():
            return

        menu_bar = get_app().menu_bars[1]
        self.roots = name_and_centers(menu_bar.menus)
        self.leafs = {}
        ctx.set_list('current', self.roots.keys())
        self.path = []
        return
        # TODO... menu walking
        menu_items = menubar().menus.menu_items.name()[0]

        items = []
        item_map = {}
        for i, menu in enumerate(menu_items):
            for item in menu:
                if isinstance(item, str):
                    items.append(item)
                    item_map[item] = (menu_names[i], item)

        long_items = [n for n in items if ' ' in n]
        print(menu_names)
        self.item_map = item_map
        self.path = []

        ctx.set_list('current', menu_names)
        # ctx.set_list('all_items', items)
        # ctx.set_list('long_items', long_items)

    def click(self, m):
        print(m)

    def descend(self, m):
        ctx.set_list('current', self.roots.keys())
        word = str(m['menus.current'][0])
#         print(word, self.path)
        new_menu = False
        if word in self.roots:
            if self.path:
                new_menu = True
            self.path = [word]
        elif word == 'menu back':
            self.path.pop()
        else:
            self.path.append(word)

        if word == 'menu cancel' or word == 'menu back' and not self.path:
            ctrl.key_press('escape')
            self.update()
            return

        pos = self.roots.get(word) or self.leafs.get(word)
        if pos and False:
            x, y = map(int, pos)
            ctrl.mouse(x, y)
            if not new_menu:
                ctrl.mouse_click()
        app = get_app()
        cur, menu = get_menu(app.menu_bars[1], self.path)
        if not pos or True:
            if new_menu:
                ctrl.key_press('escape')
            cur.click()
        self.leafs = name_and_centers(menu.menu_items)

        if self.leafs:
#             print(self.leafs)
            ctx.set_list('current', list(self.leafs.keys()) + ['menu back', 'menu cancel'] + list(self.roots.keys()))
        else:
            self.update()

watcher = MenuWatcher()
ctx = Context('menus')
ctx.keymap({
    # 'menu {menus.all_items}': watcher.click,
    # '{menus.long_items}': watcher.click,
    'menu {menus.current}': watcher.descend,
})
watcher.update()
