
import os

## To enable trace debugging...
# os.environ['PYGLAME_DEBUG_TRACE'] = 'TRUE'
os.environ['PYGLAME_DEBUG_TRACE_ARGS'] = 'TRUE'
os.environ['PYGLAME_DEBUG_TRACE_DEPTH'] = '1'

import math
import pygame

import pyglame

import pyglame.window.event

class MyScene(object):
    def __init__(self, window):
        self.window = window
        self.frame = 0
        self.r1 = 0
        self.r2 = 0
        self.start_time = None
        self.rt = 0

    def activate(self):
        self.window.push_handlers(self)
        pyglame.clock.schedule(self.on_update)

    def deactivate(self):
        pyglame.clock.unschedule(self.on_update)
        self.window.pop_handlers()

    def on_draw(self):
        window = self.window
        surface = window.surface
        surface.surface.fill(0)

        pi2 = math.pi * 2
        pihalf = math.pi / 2

        length = max(((min(window.width, window.height) / 2) - 5), 10)
        center = (window.width / 2, window.height / 2)

        ## TODO: Finish pyglame.draw API
        # Do something...
        pygame.draw.rect(
            surface.surface,
            pygame.Color(240, 240, 240),
            (10, 10, window.width-20, window.height-20),
            0)

        pygame.draw.line(
            surface.surface, pygame.Color(255, 128, 0),
            center,
            (   int(center[0] + (math.cos(self.r1 * pi2 - pihalf) * (length-7))),
                int(center[1] + (math.sin(self.r1 * pi2 - pihalf) * (length-7)))),
            5)

        pygame.draw.line(
            surface.surface, pygame.Color(128, 128, 128),
            center,
            (   int(center[0] + (math.cos(self.r2 * pi2 - pihalf) * length)),
                int(center[1] + (math.sin(self.r2 * pi2 - pihalf) * length))),
            1)

        pygame.draw.line(
            surface.surface, pygame.Color(0, 128, 0),
            center,
            (   int(center[0] + (math.cos(self.rt * pi2 - pihalf) * (length - 20))),
                int(center[1] + (math.sin(self.rt * pi2 - pihalf) * (length - 20)))),
            1)

        return True

    def on_update(self, dt):
        if self.start_time == None:
            self.start_time = pyglame.clock._default_time_function() - dt

        self.rt = (pyglame.clock._default_time_function() - self.start_time) * (1/60.)
        self.rt %= 360

        self.window.set_caption("Testing! - {:5.2f} fps".format(pyglame.clock.get_fps()))
        self.frame += 1

        self.r1 += dt * (1/60.)
        self.r2 += dt * (1/30.)
        self.r1 %= 360
        self.r2 %= 360

        diff = abs(self.rt - self.r1)
        if diff > 0.1:
            print "DIFF: {}".format(diff)

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglame.window.key.RETURN and (
                modifiers & pyglame.window.key.MOD_ALT):
            self.window.set_fullscreen(not self.window.fullscreen)

    def on_deactivate(self):
        pyglame.clock.set_fps_limit(10)

    def on_activate(self):
        pyglame.clock.set_fps_limit(30)

    def on_show(self):
        # Start drawing again :)
        self.window.invalid = True

    def on_hide(self):
        # Stop drawing, updates keep going.
        self.window.invalid = False


def main():
    window = pyglame.window.Window(640, 480, resizable=True)
    window.set_minimum_size(200, 200)

    scene = MyScene(window)
    scene.activate()

    window.push_handlers(pyglame.window.event.WindowEventLogger())

    pyglame.clock.set_fps_limit(30)
    pyglame.app.run()

if __name__ == '__main__':
    main()
