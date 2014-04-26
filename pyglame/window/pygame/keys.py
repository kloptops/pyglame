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

from pyglame.window import key
import pygame

_translate_modifiers_cache = {}
def translate_modifiers(in_modifier):
    global _translate_modifiers_cache
    if in_modifier in _translate_modifiers_cache:
        return _translate_modifiers_cache[in_modifier]

    out_modifier = 0
    if in_modifier & pygame.KMOD_SHIFT:
        out_modifier |= key.MOD_SHIFT
    if in_modifier & pygame.KMOD_CTRL:
        out_modifier |= key.MOD_CTRL
    if in_modifier & pygame.KMOD_ALT:
        out_modifier |= key.MOD_ALT
    if in_modifier & pygame.KMOD_CAPS:
        out_modifier |= key.MOD_CAPSLOCK
    if in_modifier & pygame.KMOD_NUM:
        out_modifier |= key.MOD_NUMLOCK
    ## TODO: add meta modifier?
    # if in_modifier & pygame.KMOD_META:
    #     out_modifier |= key.MOD_META
    _translate_modifiers_cache[in_modifier] = out_modifier
    return out_modifier

keymap = {
    # pygame.K_ASCIITILDE   : key.ASCIITILDE,    
    # pygame.K_BAR          : key.BAR,
    # pygame.K_BRACELEFT    : key.BRACELEFT,
    # pygame.K_BRACERIGHT   : key.BRACERIGHT,
    # pygame.K_EURO         : key.EURO,
    # pygame.K_MODE         : key.MODE,
    # pygame.K_PERCENT      : key.PERCENT,
    # pygame.K_POWER        : key.POWER,
    # pygame.K_QUOTELEFT    : key.QUOTELEFT,
    pygame.K_0            : key._0,
    pygame.K_1            : key._1,
    pygame.K_2            : key._2,
    pygame.K_3            : key._3,
    pygame.K_4            : key._4,
    pygame.K_5            : key._5,
    pygame.K_6            : key._6,
    pygame.K_7            : key._7,
    pygame.K_8            : key._8,
    pygame.K_9            : key._9,
    pygame.K_a            : key.A,
    pygame.K_b            : key.B,
    pygame.K_c            : key.C,
    pygame.K_d            : key.D,
    pygame.K_e            : key.E,
    pygame.K_f            : key.F,
    pygame.K_g            : key.G,
    pygame.K_h            : key.H,
    pygame.K_i            : key.I,
    pygame.K_j            : key.J,
    pygame.K_k            : key.K,
    pygame.K_l            : key.L,
    pygame.K_m            : key.M,
    pygame.K_n            : key.N,
    pygame.K_o            : key.O,
    pygame.K_p            : key.P,
    pygame.K_q            : key.Q,
    pygame.K_r            : key.R,
    pygame.K_s            : key.S,
    pygame.K_t            : key.T,
    pygame.K_u            : key.U,
    pygame.K_v            : key.V,
    pygame.K_w            : key.W,
    pygame.K_x            : key.X,
    pygame.K_y            : key.Y,
    pygame.K_z            : key.Z,
    pygame.K_AMPERSAND    : key.AMPERSAND,
    pygame.K_ASTERISK     : key.ASTERISK,
    pygame.K_AT           : key.AT,
    pygame.K_BACKQUOTE    : key.GRAVE,
    pygame.K_BACKSLASH    : key.BACKSLASH,
    pygame.K_BACKSPACE    : key.BACKSPACE,
    pygame.K_BREAK        : key.BREAK,
    pygame.K_CAPSLOCK     : key.CAPSLOCK,
    pygame.K_CARET        : key.ASCIICIRCUM,
    pygame.K_CLEAR        : key.CLEAR,
    pygame.K_COLON        : key.COLON,
    pygame.K_COMMA        : key.COMMA,
    pygame.K_DELETE       : key.DELETE,
    pygame.K_DOLLAR       : key.DOLLAR,
    pygame.K_DOWN         : key.DOWN,
    pygame.K_END          : key.END,
    pygame.K_EQUALS       : key.EQUAL,
    pygame.K_ESCAPE       : key.ESCAPE,
    pygame.K_EXCLAIM      : key.EXCLAMATION,
    pygame.K_F1           : key.F1,
    pygame.K_F10          : key.F10,
    pygame.K_F11          : key.F11,
    pygame.K_F12          : key.F12,
    pygame.K_F13          : key.F13,
    pygame.K_F14          : key.F14,
    pygame.K_F15          : key.F15,
    pygame.K_F2           : key.F2,
    pygame.K_F3           : key.F3,
    pygame.K_F4           : key.F4,
    pygame.K_F5           : key.F5,
    pygame.K_F6           : key.F6,
    pygame.K_F7           : key.F7,
    pygame.K_F8           : key.F8,
    pygame.K_F9           : key.F9,
    pygame.K_GREATER      : key.GREATER,
    pygame.K_HASH         : key.HASH,
    pygame.K_HELP         : key.HELP,
    pygame.K_HOME         : key.HOME,
    pygame.K_INSERT       : key.INSERT,
    pygame.K_KP0          : key.NUM_0,
    pygame.K_KP1          : key.NUM_1,
    pygame.K_KP2          : key.NUM_2,
    pygame.K_KP3          : key.NUM_3,
    pygame.K_KP4          : key.NUM_4,
    pygame.K_KP5          : key.NUM_5,
    pygame.K_KP6          : key.NUM_6,
    pygame.K_KP7          : key.NUM_7,
    pygame.K_KP8          : key.NUM_8,
    pygame.K_KP9          : key.NUM_9,
    pygame.K_KP_DIVIDE    : key.NUM_DIVIDE,
    pygame.K_KP_ENTER     : key.NUM_ENTER,
    pygame.K_KP_EQUALS    : key.NUM_EQUAL,
    pygame.K_KP_MINUS     : key.NUM_SUBTRACT,
    pygame.K_KP_MULTIPLY  : key.NUM_MULTIPLY,
    pygame.K_KP_PERIOD    : key.NUM_DECIMAL,
    pygame.K_KP_PLUS      : key.NUM_ADD,
    pygame.K_LALT         : key.LALT,
    pygame.K_LCTRL        : key.LCTRL,
    pygame.K_LEFT         : key.LEFT,
    pygame.K_LEFTBRACKET  : key.BRACKETLEFT,
    pygame.K_LEFTPAREN    : key.PARENLEFT,
    pygame.K_LESS         : key.LESS,
    pygame.K_LMETA        : key.LMETA,
    pygame.K_LSHIFT       : key.LSHIFT,
    pygame.K_LSUPER       : key.LWINDOWS,
    pygame.K_MENU         : key.MENU,
    pygame.K_MINUS        : key.MINUS,
    pygame.K_NUMLOCK      : key.NUMLOCK,
    pygame.K_PAGEDOWN     : key.PAGEDOWN,
    pygame.K_PAGEUP       : key.PAGEUP,
    pygame.K_PAUSE        : key.PAUSE,
    pygame.K_PERIOD       : key.PERIOD,
    pygame.K_PLUS         : key.PLUS,
    pygame.K_PRINT        : key.PRINT,
    pygame.K_QUESTION     : key.QUESTION,
    pygame.K_QUOTE        : key.APOSTROPHE,
    pygame.K_QUOTEDBL     : key.DOUBLEQUOTE,
    pygame.K_RALT         : key.RALT,
    pygame.K_RCTRL        : key.RCTRL,
    pygame.K_RETURN       : key.RETURN,
    pygame.K_RIGHT        : key.RIGHT,
    pygame.K_RIGHTBRACKET : key.BRACKETRIGHT,
    pygame.K_RIGHTPAREN   : key.PARENRIGHT,
    pygame.K_RMETA        : key.RMETA,
    pygame.K_RSHIFT       : key.RSHIFT,
    pygame.K_RSUPER       : key.RWINDOWS,
    pygame.K_SCROLLOCK    : key.SCROLLLOCK,
    pygame.K_SEMICOLON    : key.SEMICOLON,
    pygame.K_SLASH        : key.SLASH,
    pygame.K_SPACE        : key.SPACE,
    pygame.K_SYSREQ       : key.SYSREQ,
    pygame.K_TAB          : key.TAB,
    pygame.K_UNDERSCORE   : key.UNDERSCORE,
    pygame.K_UP           : key.UP,
    }
