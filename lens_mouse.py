
"""
Control your mouse cursor with your tobii eye tracker. This is an alternative to the default "Eye Tracking > Control Mouse" method.

It shows a dim circle (that looks kind of like a lens) wherever you look, instead of always moving the mouse cursor where you look. Only when you "click" does it move the mouse cursor to where the circle is, and do a mouse click. I found having the mouse cursor always moving to be distracting, and so prefer this mode.

By default, pressing F3 does the click. I did it this way because I use a separate noise recognition tool to make my clicking sound. You may want to map the click() method in this file to the "pop" sound (see https://github.com/dwiel/talon_community/blob/master/noise/pop.py)
"""

import time
import math

from talon import canvas, ctrl, tap, ui
from talon.track.geom import Point2d, EyeFrame
# from talon.track.filter import DwellFilter, LowPassFilter, MultiFilter, OneEuroFilter
# from talon.skia import Shader
from talon_plugins import eye_mouse
from talon_plugins.eye_mouse import tracker
from talon.voice import Context, Key, press

import json
from .utils import tell_hammerspoon_osa, debounce

# from .noise import model as noise_model

screen = ui.main_screen()
size_px = Point2d(screen.width, screen.height)

transparent = '01'
not_transparent = '40'

regular_size = 7
demo_size = 30

last_click = None

# Shows crazy circles
def smooth_location():

    # Calculate smooth location of point
    x = mouse.origin.x
    y = mouse.origin.y
    n = 75
    if len(mouse.xy_hist) < n: n = len(mouse.xy_hist)
    total = 1
    minimum_group = 4
    for i in range(n):
        x2 = mouse.xy_hist[-1 - i].x
        y2 = mouse.xy_hist[-1 - i].y

        # If there are at least 5 points (so there's some smoothness)
        if i > minimum_group:
            # Don't use if points are really far away, so long moves are fast
            if abs(x2-mouse.origin.x) > 60: continue
            if abs(y2-mouse.origin.y) > 60: continue

        x += x2
        y += y2
        total += 1

    x /= total
    y /= total
    return [x, y]


class LensMouse:
    def __init__(self):


        self.xy_hist = [Point2d(0, 0)]
        self.origin = Point2d(0, 0)

        # tracker.register('gaze', self.on_gaze)
        # canvas.register('overlay', self.draw)

        self.enabled = False
        self.alpha = not_transparent
        self.size = regular_size

    def draw(self, canvas: canvas.SkCanvas):

        if mouse.origin == None:
            print("Is the tobii disconnected?")
            return
            
        # # avoid drawing distracting circle
        # if mouse.alpha == transparent:
        #     return

        pos = smooth_location()

        # Append the smoothed dot to history > to smooth it some more
        mouse.xy_hist.append(Point2d(pos[0], pos[1]))
        mouse.xy_hist.append(Point2d(pos[0], pos[1]))

        if pos == None: return

        paint = canvas.paint

        # paint.stroke_width = 0
        # paint.style = paint.Style.STROKE
        # paint.color = 'cbd14d40'

        # canvas.draw_circle(pos[0], pos[1], 25)

        paint.style = paint.Style.FILL
        
        now = time.time()
        if last_click is not None and now - last_click < 0.20:
            color = '044d63'
            alpha = '99'
        else:
            color = 'cbd14d'
            alpha = self.alpha
            
        paint.color = color + alpha
        # canvas.draw_circle(pos[0], pos[1], 25)
        canvas.draw_circle(pos[0], pos[1], self.size)
        # if noise_model.dragging:
        #     ctrl.mouse_move(pos[0], pos[1])

    def on_gaze(self, b):
        # print(b)
        l = b["Left Eye 2D Gaze Point"]['$point2d']
        r = b["Right Eye 2D Gaze Point"]['$point2d']

        x = (l["x"] + r["x"]) / 2
        y = (l["y"] + r["y"]) / 2

        # Don't pass edges of screen
        if x < 0: x = 0
        if y < 0: y = 0

        # Multiply by screen width
        x *= size_px.x
        y *= size_px.y

        self.origin = Point2d(x, y)
        self.xy_hist.append(self.origin)
        self.xy_hist = self.xy_hist[-200:]
        self.update_hammerspoon()
    
    @debounce(2.5)
    def update_hammerspoon(self):
        eyes_json = json.dumps(list(map(pointToObj, self.xy_hist[-3:])))
        eyes_json = eyes_json.replace('"', '\\"')
        tell_hammerspoon_osa(f"eyeHistory('{eyes_json}')")
        
        
def pointToObj(point):
    return {'x':point.x, 'y': point.y}

def click():
    pos = smooth_location()
    ctrl.mouse_move(pos[0], pos[1])
    ctrl.mouse_click(button=0, hold=16000)
    last_click = time.time()

def on_key(tap, e):

    # Only do something on key down
    if not e.down: return

    # F3 means click
    if e == "f3":
        e.block()
        click()

    # option+= means toggle tobii on and off.
    elif e == "alt-=":
        e.block()
        toggle_watcher()

tap.register(tap.KEY | tap.HOOK, on_key)

# Uncomment to enable
mouse = LensMouse()

context = Context("lens_mouse")

def toggle_watcher():
    if mouse.enabled:
        # print("    unregister")
        tracker.unregister('gaze', mouse.on_gaze)
        canvas.unregister('overlay', mouse.draw)
        # lens mode is useless without eye tracking
        # noise_model.lens_mode = False
    else:
        # print("    register")
        tracker.register('gaze', mouse.on_gaze)
        
        # turn circle back on if it was on previously?
        if mouse.alpha == not_transparent:
            canvas.register('overlay', mouse.draw)
            
    mouse.enabled = not mouse.enabled

def toggle_circle():
    mouse.alpha = not_transparent if mouse.alpha == transparent else transparent
    if mouse.alpha == transparent:
        canvas.unregister('overlay', mouse.draw)
    else:
        canvas.register('overlay', mouse.draw)

def toggle_demo():
    mouse.size = demo_size if mouse.size == regular_size else regular_size

context.keymap(
    {
        # "shit": lambda m: mouse.enabled and click(),
        "(kill | toggle) circle": lambda m: mouse.enabled and toggle_circle(),
        "(kill | toggle) eyes": lambda m: toggle_watcher(),
        "presentation mode": lambda m: mouse.enabled and toggle_demo(),
        # old stuff
        'control mouse':   lambda m: eye_mouse.control_mouse.toggle(),
        'camera overlay':  lambda m: eye_mouse.camera_overlay.toggle(),
        'run calibration': lambda m: eye_mouse.calib_start(),
        'calibrate eyes': lambda m: eye_mouse.calib_start(),
    }
)