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

'''Mouse constants and utilities for pyglet.window.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

def buttons_string(buttons):
    '''Return a string describing a set of active mouse buttons.

    Example::

        >>> buttons_string(LEFT | RIGHT)
        'LEFT|RIGHT'

    :Parameters:
        `buttons` : int
            Bitwise combination of mouse button constants.

    :rtype: str
    '''
    button_names = []
    if buttons & LEFT:
        button_names.append('LEFT')
    if buttons & MIDDLE:
        button_names.append('MIDDLE')
    if buttons & RIGHT:
        button_names.append('RIGHT')

    if buttons & SCROLL_UP:
        button_names.append('SCROLL_UP')
    if buttons & SCROLL_DOWN:
        button_names.append('SCROLL_DOWN')

    if buttons & BUTTON_6:
        button_names.append('BUTTON_6')
    if buttons & BUTTON_7:
        button_names.append('BUTTON_7')
    if buttons & BUTTON_8:
        button_names.append('BUTTON_8')
    if buttons & BUTTON_9:
        button_names.append('BUTTON_9')

    return '|'.join(button_names)

# Symbolic names for the mouse buttons
LEFT =   1 << 0
MIDDLE = 1 << 1
RIGHT =  1 << 2
SCROLL_UP   = 1<<3
SCROLL_DOWN = 1<<4

BUTTON_1 = LEFT
BUTTON_2 = MIDDLE
BUTTON_3 = RIGHT
BUTTON_4 = SCROLL_UP
BUTTON_5 = SCROLL_DOWN
BUTTON_6 = 1<<5
BUTTON_7 = 1<<6
BUTTON_8 = 1<<7
BUTTON_9 = 1<<8
