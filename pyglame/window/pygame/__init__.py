# ----------------------------------------------------------------------------
#
# pyglame
# Copyright (c) 2014 Jacob Smith
#
# pyglet event emulation layer for pygame.
#
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import sys
import unicodedata

import pygame

from pyglame.window import (
    BaseWindow,
    Platform, Display, Screen,
    MouseCursor, DefaultMouseCursor, WindowException)
from pyglame.event import EventDispatcher
from pyglame.window import key, mouse
from pyglame.window.pygame.keys import (
    keymap as _keymap,
    translate_modifiers as _translate_modifiers)
from pyglame.window.pygame.cursors import cursors as _cursors


class PygameWindowException(WindowException):
    pass


if sys.platform == 'darwin':
    ## TODO: test these! :D
    # Map symbol,modifiers -> motion
    # Determined by experiment with TextEdit.app
    _motion_map = {
        (key.UP,        False):             key.MOTION_UP,
        (key.RIGHT,     False):             key.MOTION_RIGHT,
        (key.DOWN,      False):             key.MOTION_DOWN,
        (key.LEFT,      False):             key.MOTION_LEFT,
        (key.LEFT,      key.MOD_OPTION):    key.MOTION_PREVIOUS_WORD,
        (key.RIGHT,     key.MOD_OPTION):    key.MOTION_NEXT_WORD,
        (key.LEFT,      key.MOD_COMMAND):   key.MOTION_BEGINNING_OF_LINE,
        (key.RIGHT,     key.MOD_COMMAND):   key.MOTION_END_OF_LINE,
        (key.PAGEUP,    False):             key.MOTION_PREVIOUS_PAGE,
        (key.PAGEDOWN,  False):             key.MOTION_NEXT_PAGE,
        (key.HOME,      False):             key.MOTION_BEGINNING_OF_FILE,
        (key.END,       False):             key.MOTION_END_OF_FILE,
        (key.UP,        key.MOD_COMMAND):   key.MOTION_BEGINNING_OF_FILE,
        (key.DOWN,      key.MOD_COMMAND):   key.MOTION_END_OF_FILE,
        (key.BACKSPACE, False):             key.MOTION_BACKSPACE,
        (key.DELETE,    False):             key.MOTION_DELETE,
        }
else: # sys.platform in ('win32', 'cygwin', 'linux'):
    # Map symbol,modifiers -> motion
    _motion_map = {
        (key.UP,        False):             key.MOTION_UP,
        (key.RIGHT,     False):             key.MOTION_RIGHT,
        (key.DOWN,      False):             key.MOTION_DOWN,
        (key.LEFT,      False):             key.MOTION_LEFT,
        (key.RIGHT,     key.MOD_CTRL):      key.MOTION_NEXT_WORD,
        (key.LEFT,      key.MOD_CTRL):      key.MOTION_PREVIOUS_WORD,
        (key.HOME,      False):             key.MOTION_BEGINNING_OF_LINE,
        (key.END,       False):             key.MOTION_END_OF_LINE,
        (key.PAGEUP,    False):             key.MOTION_PREVIOUS_PAGE,
        (key.PAGEDOWN,  False):             key.MOTION_NEXT_PAGE,
        (key.HOME,      key.MOD_CTRL):      key.MOTION_BEGINNING_OF_FILE,
        (key.END,       key.MOD_CTRL):      key.MOTION_END_OF_FILE,
        (key.BACKSPACE, False):             key.MOTION_BACKSPACE,
        (key.DELETE,    False):             key.MOTION_DELETE,
        }


class PygamePlatform(Platform):
    _display = None

    def get_default_display(self):
        if not self._display:
            self._display = PygameDisplay()
        return self._display


class PygameDisplay(Display):
    def __init__(self):
        from pyglame import app
        app.displays.add(self)
        if len(app.displays) == 1:
            pygame.init()
            pygame.key.set_repeat(50, 50)

    # def __del__(self):
    #     from pyglame import app
    #     if len(app.displays) == 1 and self in app.displays:
    #         pygame.quit()

    def get_screens(self):
        size = pygame.display.list_modes()[0]
        return [PygameScreen(0, 0, size[0], size[1])]


class PygameScreen(Screen):
    pass


class PygameCursor(MouseCursor):
    drawable = False

    def __init__(self, cursor_info):
        assert isinstance(cursor_info, (tuple, list))
        assert len(cursor_info) == 3

        self._mouse_info = (
            cursor_info[:2] + pygame.cursors.compile(cursor_info[2]))


_pygame_default_mouse = PygameCursor(_cursors['arrow'])
_cursor_cache = {}

class PygameWindow(BaseWindow):

    _surface      = None

    _fullscreen_modes = (
        ## TODO: fullscreen resizeable sort of doesn't really not sort of work.
        pygame.FULLSCREEN|pygame.HWSURFACE|pygame.RESIZABLE|pygame.DOUBLEBUF,
        pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF,
        pygame.FULLSCREEN|pygame.RESIZABLE,
        pygame.FULLSCREEN,
        )

    def __init__(self, *args, **kwargs):
        from pyglame import app

        self._pressed = {}
        self._minimum_size = None
        self._maximum_size = None

        if len(app.windows) > 0:
            raise PygameWindowException('Only one Pyglame window may appear at a time!')

        super(PygameWindow, self).__init__(*args, **kwargs)

        self._last_mouse_cursor = None
        self._last_mouse_visible = None
        self.set_mouse_platform_visible()
        self.dispatch_event('on_resize', self._width, self._height)
        self.dispatch_event('on_show')

    def _create(self):
        size = (self._width, self._height)
        if self._fullscreen:
            for fullscreen_mode in self._fullscreen_modes:
                if pygame.display.mode_ok(size, fullscreen_mode):
                    break
            else:
                raise PygameWindowException("Unable to go fullscreen")

            self._surface = pygame.display.set_mode(
                size, fullscreen_mode)
        else:
            if not pygame.display.mode_ok(
                    size, pygame.RESIZABLE if self._resizable else 0):
                raise PygameWindowException("Unable to create pygame window")

            self._surface = pygame.display.set_mode(
                size, pygame.RESIZABLE if self._resizable else 0)


    def _recreate(self, changes):
        self._create()

    def switch_to(self):
        pass

    def activate(self):
        self.dispatch_event('on_activate')

    ## Set size stuff
    def set_size(self, width, height):
        if width == self._width and height == self._height:
            return

        if self._fullscreen == False:
            print "Before: ", width, height
            if self._minimum_size:
                width  = max(width, self._minimum_size[0])
                height = max(height, self._minimum_size[1])
            if self._maximum_size:
                width  = min(width, self._maximum_size[0])
                height = min(height, self._maximum_size[1])
            print "After: ", width, height

        self._width = width
        self._height = height
        self._recreate(['resize'])
        self.dispatch_event('on_resize', width, height)

    def get_size(self):
        return self._width, self._height

    def set_minimum_size(self, width, height):
        if width is None or height is None:
            self._minimum_size = None
        self._minimum_size = width, height

    def set_maximum_size(self, width, height):
        if width is None or height is None:
            self._maximum_size = None
        self._maximum_size = width, height

    ## Drawing stuffs
    def clear(self):
        self._surface.fill(0)

    def flip(self):
        pygame.display.update()

    def set_caption(self, caption):
        self._caption = caption
        if caption != None:
            pygame.display.set_caption(caption)

    ## MOUSE STUFFS
    def set_mouse_platform_visible(self, platform_visible=None):
        if platform_visible == None:
            platform_visible = self._mouse_visible

        if (self._last_mouse_visible == platform_visible and
                self._last_mouse_cursor == self._mouse_cursor):
            return

        self._last_mouse_visible = platform_visible
        self._last_mouse_cursor = self._mouse_cursor

        if isinstance(self._mouse_cursor, DefaultMouseCursor):
            cursor = _pygame_default_mouse
        elif isinstance(self._mouse_cursor, PygameCursor):
            cursor = self._mouse_cursor
        else:
            pygame.mouse.set_visible(False)
            return

        pygame.mouse.set_cursor(*cursor._mouse_info)
        pygame.mouse.set_visible(platform_visible)

        self._last_mouse_visible
        self._last_mouse_cursor


    def get_system_mouse_cursor(self, name):
        global _cursor_cache

        if name == self.CURSOR_DEFAULT:
            return DefaultMouseCursor()

        names = {
            self.CURSOR_CROSSHAIR       : 'crosshair',
            self.CURSOR_HAND            : 'hand',
            self.CURSOR_HELP            : 'help',
            self.CURSOR_NO              : 'no',
            self.CURSOR_SIZE            : 'move',
            self.CURSOR_SIZE_UP         : 'sizer_y',
            self.CURSOR_SIZE_UP_RIGHT   : 'sizer_yx',
            self.CURSOR_SIZE_RIGHT      : 'sizer_x',
            self.CURSOR_SIZE_DOWN_RIGHT : 'sizer_xy',
            self.CURSOR_SIZE_DOWN       : 'sizer_y',
            self.CURSOR_SIZE_DOWN_LEFT  : 'sizer_yx',
            self.CURSOR_SIZE_LEFT       : 'sizer_x',
            self.CURSOR_SIZE_UP_LEFT    : 'sizer_xy',
            self.CURSOR_SIZE_UP_DOWN    : 'sizer_y',
            self.CURSOR_SIZE_LEFT_RIGHT : 'sizer_x',
            self.CURSOR_TEXT            : 'text',
            self.CURSOR_WAIT            : 'wait',
            self.CURSOR_WAIT_ARROW      : 'wait_arrow',
            }

        if name not in names:
            raise PygameWindowException(
                'Unknown cursor name {}'.format(name))

        if names[name] in _cursor_cache:
            return _cursor_cache[names[name]]
        else:
            cursor_info = _cursors[names[name]]
            cursor = PygameCursor(cursor_info)
            _cursor_cache[names[name]] = cursor
            return cursor


    def dispatch_events(self):
        self._allow_dispatch_event = True
        self.dispatch_pending_events()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.dispatch_event('on_close')

            elif event.type == pygame.VIDEORESIZE:
                self.set_size(event.w, event.h)
                ## Handled by set_size :D
                # self.dispatch_event('on_resize', event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                ## TODO: make sure we're really getting it right here...
                pyglame_key = _keymap.get(event.key, None)
                pyglame_mod = _translate_modifiers(event.mod)

                if pyglame_key == None:
                    print "Unknown key: {} ({})".format(
                        event.key, pygame.key.name(event.key))

                if pyglame_key != None and event.key not in self._pressed:
                    self._pressed[event.key] = True

                    self.dispatch_event(
                        'on_key_press', pyglame_key, pyglame_mod)

                motion_mod = pyglame_mod & ~(key.MOD_SHIFT|key.MOD_NUMLOCK|key.MOD_CAPSLOCK)
                if (pyglame_key, motion_mod) in _motion_map:
                    motion_key = _motion_map[(pyglame_key, motion_mod)]
                    if pyglame_mod & key.MOD_SHIFT:
                        self.dispatch_event('on_text_motion_select', motion_key)
                    else:
                        self.dispatch_event('on_text_motion', motion_key)

                if event.unicode != '' and (
                        not pyglame_mod & ~(key.MOD_SHIFT|key.MOD_NUMLOCK|key.MOD_CAPSLOCK)):

                    if unicodedata.category(event.unicode) != 'Cc' or event.unicode == '\r':
                        self.dispatch_event('on_text', event.unicode)

            elif event.type == pygame.KEYUP:
                pyglame_key = _keymap.get(event.key, None)
                pyglame_mod = _translate_modifiers(event.mod)

                if pyglame_key == None:
                    print "Unknown key: {} ({})".format(
                        event.key, pygame.key.name(event.key))

                if pyglame_key != None and event.key in self._pressed:
                    del self._pressed[event.key]

                    self.dispatch_event(
                        'on_key_release', pyglame_key, pyglame_mod)

            elif event.type == pygame.ACTIVEEVENT:
                ## BUG: In Ubuntu it doesn't seem to ever do on_hide/on_show...
                ## It should go on_deactivate() then on_hide()
                ##   in reverse do: on_show() then on_activate()
                if event.gain == 0 and event.state & 2:
                    self.dispatch_event('on_deactivate')
                if event.gain == 0 and event.state & 4:
                    self.dispatch_event('on_hide')
                if event.gain == 1 and event.state & 4:
                    self.dispatch_event('on_show')
                if event.gain == 1 and event.state & 2:
                    pygame.key.set_mods(
                        pygame.key.get_mods() &
                        ~(key.MOD_ALT|key.MOD_CTRL|key.MOD_SHIFT))
                    self.dispatch_event('on_activate')

                if event.gain == 0 and event.state & 1:
                    pos = pygame.mouse.get_pos()
                    self._mouse_x = pos[0]
                    self._mouse_y = pos[1]
                    self._mouse_in_window = True

                    self.dispatch_event('on_mouse_leave', pos[0], pos[1])
                if event.gain == 1 and event.state & 1:
                    pos = pygame.mouse.get_pos()
                    self._mouse_x = pos[0]
                    self._mouse_y = pos[1]
                    self._mouse_in_window = True

                    pos = pygame.mouse.get_pos()
                    self.dispatch_event('on_mouse_enter', pos[0], pos[1])

            elif event.type == pygame.MOUSEMOTION:
                self._mouse_x = event.pos[0]
                self._mouse_y = event.pos[1]
                if not self._mouse_in_window:
                    self._mouse_in_window = True
                    self.dispatch_event('on_mouse_enter', event.pos[0], event.pos[1])

                if event.buttons == (0, 0, 0):
                    self.dispatch_event(
                        'on_mouse_motion',
                        event.pos[0], event.pos[1],
                        event.rel[0], event.rel[1])
                else:
                    buttons = event.buttons[0]|event.buttons[1]<<1|event.buttons[2]<<2
                    mods = _translate_modifiers(pygame.key.get_mods())
                    self.dispatch_event(
                        'on_mouse_drag',
                        event.pos[0], event.pos[1],
                        event.rel[0], event.rel[1],
                        buttons,
                        mods)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_x = event.pos[0]
                self._mouse_y = event.pos[1]
                if not self._mouse_in_window:
                    self._mouse_in_window = True
                    self.dispatch_event('on_mouse_enter', event.pos[0], event.pos[1])

                button = (1<<event.button-1)
                mods = _translate_modifiers(pygame.key.get_mods())
                self.dispatch_event(
                    'on_mouse_press',
                    event.pos[0], event.pos[1],
                    button,
                    mods)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_x = event.pos[0]
                self._mouse_y = event.pos[1]
                if not self._mouse_in_window:
                    self._mouse_in_window = True
                    self.dispatch_event('on_mouse_enter', event.pos[0], event.pos[1])

                button = (1<<event.button-1)
                mods = _translate_modifiers(pygame.key.get_mods())
                self.dispatch_event(
                    'on_mouse_release',
                    event.pos[0], event.pos[1],
                    (1<<event.button-1),
                    mods)

            ## Don't have a joystick atm, so this cant be tested... :(
            # elif event.type == pygame.JOYAXISMOTION:
            #     print "JOYAXISMOTION: joy: {}, axis: {}, value: {}".format(
            #         event.joy, event.axis, event.value)
            # elif event.type == pygame.JOYBALLMOTION:
            #     print "JOYBALLMOTION: joy: {}, ball: {}, rel: {}".format(
            #         event.joy, event.ball, event.rel)
            # elif event.type == pygame.JOYHATMOTION:
            #     print "JOYHATMOTION: joy: {}, hat: {}, value: {}".format(
            #         event.joy, event.hat, event.value)
            # elif event.type == pygame.JOYBUTTONUP:
            #     print "JOYBUTTONUP: joy: {}, button: {}".format(
            #         event.joy, event.button)
            # elif event.type == pygame.JOYBUTTONDOWN:
            #     print "JOYBUTTONDOWN: joy: {}, button: {}".format(
            #         event.joy, event.button)

        self._allow_dispatch_event = False

    def dispatch_pending_events(self):
        while self._event_queue:
            event = self._event_queue.popleft()
            # pyglame event
            EventDispatcher.dispatch_event(self, *event)
