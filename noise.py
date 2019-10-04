import time

from talon import ctrl
from talon import tap
from talon.audio import noise
from talon.track.geom import Point2d
from talon_plugins import eye_zoom_mouse
from talon.voice import Context, Key, press
from .utils import tell_hammerspoon_osa
try:
    from . import lens_mouse
except AttributeError:
    lens_mouse = False

class NoiseModel:
    def __init__(self):
        self.hiss_start = 0
        self.hiss_last = 0
        self.button = 0
        self.mouse_origin = Point2d(0, 0)
        self.mouse_last = Point2d(0, 0)
        self.dragging = False
        self.short_click = True
        self.morse_mode = False
        self.lens_mode = False
        # # do we auto-start?
        # self.start()

    def start(self):
        tap.register(tap.MMOVE, self.on_move)
        noise.register('noise', self.on_noise)

    def stop(self):
        tap.unregister(tap.MMOVE, self.on_move)
        noise.unregister('noise', self.on_noise)

    def on_move(self, typ, e):
        if typ != tap.MMOVE or self.morse_mode or self.lens_mode: return
        
        self.mouse_last = pos = Point2d(e.x, e.y)
        if self.hiss_start and not self.dragging:
            if (pos - self.mouse_origin).len() > 10:
                self.dragging = True
                self.button = 0
                x, y = self.mouse_origin.x, self.mouse_origin.y
                ctrl.mouse(x, y)
                ctrl.mouse_click(x, y, button=0, down=True)

    def on_noise(self, noise):
        now = time.time()
        if noise == 'pop' and not eye_zoom_mouse.zoom_mouse.enabled:
            ctrl.mouse_click(button=0, hold=16000)
        elif noise == 'hiss_start':
            if not self.morse_mode and not self.lens_mode:
                if now - self.hiss_last < 0.25:
                    ctrl.mouse_click(button=self.button, down=True)
                    self.hiss_last = now
                    self.dragging = True
                else:
                    self.mouse_origin = self.mouse_last
            self.hiss_start = now
        elif noise == 'hiss_end':
            if self.morse_mode:
                duration = (time.time() - self.hiss_start) * 1000
                tell_hammerspoon_osa(f'trackMorse({duration})')
                self.hiss_last = now
            elif self.lens_mode:
                duration = time.time() - self.hiss_start
                if duration > 0.12 and lens_mouse and lens_mouse.mouse.enabled:
                    lens_mouse.click()
                    self.hiss_last = now
                self.hiss_start = 0
            else:
                if self.dragging:
                    ctrl.mouse_click(button=self.button, up=True)
                    self.dragging = False
                else:
                    duration = time.time() - self.hiss_start
                    if duration > 0.5:
                        self.button = 1
                        ctrl.mouse_click(button=1)
                        self.hiss_last = now
                    elif duration > 0.12 and self.short_click:
                        self.button = 0
                        ctrl.mouse_click(button=0)
                        self.hiss_last = now
            self.hiss_start = 0

model = NoiseModel()

def start_hissing(m):
    model.start()

def stop_hissing(m):
    model.stop()

def morse_mode(m):
    model.morse_mode = not model.morse_mode
    
    if model.morse_mode:
        tell_hammerspoon_osa("speakText('Morse mode active')")
    if model.lens_mode and model.morse_mode:
        model.lens_mode = False

def hiss_lens_mode(m):
    model.lens_mode = not model.lens_mode
    if model.lens_mode:
        tell_hammerspoon_osa("speakText('Lens mode active')")
    if model.lens_mode and model.morse_mode:
        model.morse_mode = False

context = Context("noise")

context.keymap(
    {
        "(quiet | hiss stop)": stop_hissing,
        "(loud | hiss start)": start_hissing,
        "(morse mode | more smoke)": morse_mode,
        "((hiss | loud) click)": hiss_lens_mode,
        # "(hiss short click)": lambda m: model.short_click = not model.short_click,
    }
)