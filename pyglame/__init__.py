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
pyglame is a pyglet emulation layer for pygame
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys
import os

_is_epydoc = hasattr(sys, 'is_epydoc') and sys.is_epydoc

#:
#: Use setuptools if you need to check for a specific release version, e.g.::
#:
#:    >>> import pyglame
#:    >>> from pkg_resources import parse_version
#:    >>> parse_version(pyglame.version) >= parse_version('0.0.1')
#:    True
#:
version = '0.0.1'


#: Global dict of pyglame options.  To change an option from its default, you
#: must import ``pyglame`` before any sub-packages.  For example::
#:
#:      import pyglame
#:      pyglame.options['debug_gl'] = False
#:
options = {
    'debug_trace': False,
    'debug_trace_args': False,
    'debug_trace_depth': 1,
    'debug_trace_flush': True,
    'debug_trace_restrict': True,
    'debug_pyglet': False,
    }
_option_types = {
    'debug_trace': bool,
    'debug_trace_args': bool,
    'debug_trace_depth': int,
    'debug_trace_flush': bool,
    'debug_trace_restrict': bool,
    'debug_pyglet': bool,
    }


def _read_environment():
    '''Read defaults for options from environment'''
    for key in options:
        env = 'PYGLAME_%s' % key.upper()
        try:
            value = os.environ[env]
            if _option_types[key] is tuple:
                options[key] = value.split(',')
            elif _option_types[key] is bool:
                options[key] = value in ('true', 'TRUE', 'True', '1')
            elif _option_types[key] is int:
                options[key] = int(value)
        except KeyError:
            pass
_read_environment()


# Call tracing
# ------------

_trace_filename_abbreviations = {}

def _trace_repr(value, size=60):
    value = repr(value)
    if len(value) > size:
        value = value[:size//2-2] + '...' + value[-size//2-1:]
    return value

def _trace_frame(frame, indent):
    code = frame.f_code
    name = code.co_name
    path = code.co_filename
    line = code.co_firstlineno

    if _trace_restrict:
        if 'pyglame' not in path:
            return

    try:
        filename = _trace_filename_abbreviations[path]
    except KeyError:
        # Trim path down
        dir = ''
        path, filename = os.path.split(path)
        while len(dir + filename) < 60:
            filename = os.path.join(dir, filename)
            path, dir = os.path.split(path)
            if not dir:
                filename = os.path.join('', filename)
                break
        else:
            filename = os.path.join('...', filename)
        _trace_filename_abbreviations[path] = filename

    location = '(%s:%d)' % (filename, line)

    if indent:
        name = 'Called from %s' % name
    print '%s%s %s' % (indent, name, location)

    if _trace_args:
        for argname in code.co_varnames[:code.co_argcount]:
            try:
                argvalue = _trace_repr(frame.f_locals[argname])
                print '  %s%s=%s' % (indent, argname, argvalue)
            except:
                pass

    if _trace_flush:
        sys.stdout.flush()

def _trace_func(frame, event, arg):
    if event == 'call':
        indent = ''
        for i in range(_trace_depth):
            _trace_frame(frame, indent)
            indent += '  '
            frame = frame.f_back
            if not frame:
                break

    elif event == 'exception':
        (exception, value, traceback) = arg
        print 'First chance exception raised:', repr(exception)

def _install_trace():
    print "Installing trace"
    sys.setprofile(_trace_func)

_trace_args = options['debug_trace_args']
_trace_depth = options['debug_trace_depth']
_trace_flush = options['debug_trace_flush']
_trace_restrict = options['debug_trace_restrict']
if options['debug_trace']:
    _install_trace()

# Lazy loading
# ------------

class _ModuleProxy(object):
    _module = None

    def __init__(self, name):
        self.__dict__['_module_name'] = name

    def __getattr__(self, name):
        try:
            return getattr(self._module, name)
        except AttributeError:
            if self._module is not None:
                raise

            import_name = 'pyglame.%s' % self._module_name
            __import__(import_name)
            module = sys.modules[import_name]
            object.__setattr__(self, '_module', module)
            globals()[self._module_name] = module
            return getattr(module, name)

    def __setattr__(self, name, value):
       try:
            setattr(self._module, name, value)
       except AttributeError:
            if self._module is not None:
                raise

            import_name = 'pyglame.%s' % self._module_name
            __import__(import_name)
            module = sys.modules[import_name]
            object.__setattr__(self, '_module', module)
            globals()[self._module_name] = module
            setattr(module, name, value)

if not _is_epydoc:
    app      = _ModuleProxy('app')
    clock    = _ModuleProxy('clock')
    draw     = _ModuleProxy('draw')
    event    = _ModuleProxy('event')
    font     = _ModuleProxy('font')
    resource = _ModuleProxy('resource')
    surface  = _ModuleProxy('surface')
    window   = _ModuleProxy('window')

# Fool py2exe, py2app into including all top-level modules (doesn't understand
# lazy loading)
if False:
    import app
    import clock
    import draw
    import event
    import font
    import resource
    import surface
    import window

# Hack around some epydoc bug that causes it to think pyglet.window is None.
if _is_epydoc:
    import window
