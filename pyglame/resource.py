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

'''Load application resources from a known path.

Loading resources by specifying relative paths to filenames is often
problematic in Python, as the working directory is not necessarily the same
directory as the application's script files.

This module allows applications to specify a search path for resources.
Relative paths are taken to be relative to the application's __main__ module.
ZIP files can appear on the path; they will be searched inside.  The resource
module also behaves as expected when applications are bundled using py2exe or
py2app.

As well as providing file references (with the `file` function), the resource
module also contains convenience functions for loading images, textures,
fonts, media and documents.

3rd party modules or packages not bound to a specific application should
construct their own `Loader` instance and override the path to use the
resources in the module's directory.

Path format
^^^^^^^^^^^

The resource path `path` (see also `Loader.__init__` and `Loader.path`)
is a list of locations to search for resources.  Locations are searched in the
order given in the path.  If a location is not valid (for example, if the
directory does not exist), it is skipped.

Locations in the path beginning with an ampersand (''@'' symbol) specify
Python packages.  Other locations specify a ZIP archive or directory on the
filesystem.  Locations that are not absolute are assumed to be relative to the
script home.  Some examples::

    # Search just the `res` directory, assumed to be located alongside the
    # main script file.
    path = ['res']

    # Search the directory containing the module `levels.level1`, followed
    # by the `res/images` directory.
    path = ['@levels.level1', 'res/images']

Paths are always case-sensitive and forward slashes are always used as path
separators, even in cases when the filesystem or platform does not do this.
This avoids a common programmer error when porting applications between
platforms.

The default path is ``['.']``.  If you modify the path, you must call
`reindex`.

:since: pyglet 1.1
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import os
import weakref
import sys
import zipfile
import StringIO

import pyglame

class ResourceNotFoundException(Exception):
    '''The named resource was not found on the search path.'''
    def __init__(self, name):
        message = ('Resource "%s" was not found on the path.  '
            'Ensure that the filename has the correct captialisation.') % name
        Exception.__init__(self, message)

def get_script_home():
    '''Get the directory containing the program entry module.

    For ordinary Python scripts, this is the directory containing the
    ``__main__`` module.  For executables created with py2exe the result is
    the directory containing the running executable file.  For OS X bundles
    created using Py2App the result is the Resources directory within the
    running bundle.

    If none of the above cases apply and the file for ``__main__`` cannot
    be determined the working directory is returned.

    :rtype: str
    '''

    frozen = getattr(sys, 'frozen', None)
    if frozen in ('windows_exe', 'console_exe'):
        return os.path.dirname(sys.executable)
    elif frozen == 'macosx_app':
        return os.environ['RESOURCEPATH']
    else:
        main = sys.modules['__main__']
        if hasattr(main, '__file__'):
            return os.path.dirname(main.__file__)

    # Probably interactive
    return ''

def get_settings_path(name):
    '''Get a directory to save user preferences.

    Different platforms have different conventions for where to save user
    preferences, saved games, and settings.  This function implements those
    conventions.  Note that the returned path may not exist: applications
    should use ``os.makedirs`` to construct it if desired.

    On Linux, a hidden directory `name` in the user's home directory is
    returned.

    On Windows (including under Cygwin) the `name` directory in the user's
    ``Application Settings`` directory is returned.

    On Mac OS X the `name` directory under ``~/Library/Application Support``
    is returned.

    :Parameters:
        `name` : str
            The name of the application.

    :rtype: str
    '''
    if sys.platform in ('cygwin', 'win32'):
        if 'APPDATA' in os.environ:
            return os.path.join(os.environ['APPDATA'], name)
        else:
            return os.path.expanduser('~/%s' % name)
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/%s' % name)
    else:
        return os.path.expanduser('~/.%s' % name)

class Location(object):
    '''Abstract resource location.

    Given a location, a file can be loaded from that location with the `open`
    method.  This provides a convenient way to specify a path to load files
    from, and not necessarily have that path reside on the filesystem.
    '''
    def open(self, filename, mode='rb'):
        '''Open a file at this location.

        :Parameters:
            `filename` : str
                The filename to open.  Absolute paths are not supported.
                Relative paths are not supported by most locations (you
                should specify only a filename with no path component).
            `mode` : str
                The file mode to open with.  Only files opened on the
                filesystem make use of this parameter; others ignore it.

        :rtype: file object
        '''
        raise NotImplementedError('abstract')

class FileLocation(Location):
    '''Location on the filesystem.
    '''
    def __init__(self, path):
        '''Create a location given a relative or absolute path.

        :Parameters:
            `path` : str
                Path on the filesystem.
        '''
        self.path = path

    def open(self, filename, mode='rb'):
        return open(os.path.join(self.path, filename), mode)

class ZIPLocation(Location):
    '''Location within a ZIP file.
    '''
    def __init__(self, zip, dir):
        '''Create a location given an open ZIP file and a path within that
        file.

        :Parameters:
            `zip` : ``zipfile.ZipFile``
                An open ZIP file from the ``zipfile`` module.
            `dir` : str
                A path within that ZIP file.  Can be empty to specify files at
                the top level of the ZIP file.

        '''
        self.zip = zip
        self.dir = dir

    def open(self, filename, mode='rb'):
        if self.dir:
            path = self.dir + '/' + filename
        else:
            path = filename
        text = self.zip.read(path)
        return StringIO.StringIO(text)

class URLLocation(Location):
    '''Location on the network.

    This class uses the ``urlparse`` and ``urllib2`` modules to open files on
    the network given a URL.
    '''
    def __init__(self, base_url):
        '''Create a location given a base URL.

        :Parameters:
            `base_url` : str
                URL string to prepend to filenames.

        '''
        self.base = base_url

    def open(self, filename, mode='rb'):
        import urlparse
        import urllib2
        url = urlparse.urljoin(self.base, filename)
        return urllib2.urlopen(url)

class Loader(object):
    '''Load program resource files from disk.

    The loader contains a search path which can include filesystem
    directories, ZIP archives and Python packages.

    :Ivariables:
        `path` : list of str
            List of search locations.  After modifying the path you must
            call the `reindex` method.
        `script_home` : str
            Base resource location, defaulting to the location of the
            application script.

    '''
    def __init__(self, path=None, script_home=None):
        '''Create a loader for the given path.

        If no path is specified it defaults to ``['.']``; that is, just the
        program directory.

        See the module documentation for details on the path format.

        :Parameters:
            `path` : list of str
                List of locations to search for resources.
            `script_home` : str
                Base location of relative files.  Defaults to the result of
                `get_script_home`.

        '''
        if path is None:
            path = ['.']
        if isinstance(path, (str, unicode)):
            path = [path]
        self.path = list(path)
        if script_home is None:
            script_home = get_script_home()
        self._script_home = script_home
        self.reindex()

        # Map name to image
        # self._cached_textures = weakref.WeakValueDictionary()
        # self._cached_images = weakref.WeakValueDictionary()
        # self._cached_animations = weakref.WeakValueDictionary()

        # Map bin size to list of atlases
        # self._texture_atlas_bins = {}

    def reindex(self):
        '''Refresh the file index.

        You must call this method if `path` is changed or the filesystem
        layout changes.
        '''
        self._index = {}
        for path in self.path:
            if path.startswith('@'):
                # Module
                name = path[1:]

                try:
                    module = __import__(name)
                except:
                    continue

                for component in name.split('.')[1:]:
                    module = getattr(module, component)

                if hasattr(module, '__file__'):
                    path = os.path.dirname(module.__file__)
                else:
                    path = '' # interactive
            elif not os.path.isabs(path):
                # Add script base unless absolute
                assert '\\' not in path, \
                    'Backslashes not permitted in relative path'
                path = os.path.join(self._script_home, path)

            if os.path.isdir(path):
                # Filesystem directory
                path = path.rstrip(os.path.sep)
                location = FileLocation(path)
                for dirpath, dirnames, filenames in os.walk(path):
                    dirpath = dirpath[len(path) + 1:]
                    # Force forward slashes for index
                    if dirpath:
                        parts = filter(None, dirpath.split(os.sep))
                        dirpath = '/'.join(parts)
                    for filename in filenames:
                        if dirpath:
                            index_name = dirpath + '/' + filename
                        else:
                            index_name = filename
                        self._index_file(index_name, location)
            else:
                # Find path component that is the ZIP file.
                dir = ''
                old_path = None
                while path and not os.path.isfile(path):
                    old_path = path
                    path, tail_dir = os.path.split(path)
                    if path == old_path:
                        break
                    dir = '/'.join((tail_dir, dir))
                if path == old_path:
                    continue
                dir = dir.rstrip('/')

                # path is a ZIP file, dir resides within ZIP
                if path and zipfile.is_zipfile(path):
                    zip = zipfile.ZipFile(path, 'r')
                    location = ZIPLocation(zip, dir)
                    for zip_name in zip.namelist():
                        #zip_name_dir, zip_name = os.path.split(zip_name)
                        #assert '\\' not in name_dir
                        #assert not name_dir.endswith('/')
                        if zip_name.startswith(dir):
                            if dir:
                                zip_name = zip_name[len(dir)+1:]
                            self._index_file(zip_name, location)

    def _index_file(self, name, location):
        if name not in self._index:
            self._index[name] = location

    def file(self, name, mode='rb'):
        '''Load a resource.

        :Parameters:
            `name` : str
                Filename of the resource to load.
            `mode` : str
                Combination of ``r``, ``w``, ``a``, ``b`` and ``t`` characters
                with the meaning as for the builtin ``open`` function.

        :rtype: file object
        '''
        try:
            location = self._index[name]
            return location.open(name, mode)
        except KeyError:
            raise ResourceNotFoundException(name)

    def location(self, name):
        '''Get the location of a resource.

        This method is useful for opening files referenced from a resource.
        For example, an HTML file loaded as a resource might reference some
        images.  These images should be located relative to the HTML file, not
        looked up individually in the loader's path.

        :Parameters:
            `name` : str
                Filename of the resource to locate.

        :rtype: `Location`
        '''
        try:
            return self._index[name]
        except KeyError:
            raise ResourceNotFoundException(name)

#: Default resource search path.
#:
#: Locations in the search path are searched in order and are always
#: case-sensitive.  After changing the path you must call `reindex`.
#:
#: See the module documentation for details on the path format.
#:
#: :type: list of str
path = []

class _DefaultLoader(Loader):
    def _get_path(self):
        return path

    def _set_path(self, value):
        global path
        path = value

    path = property(_get_path, _set_path)

_default_loader = _DefaultLoader()
reindex = _default_loader.reindex
file = _default_loader.file
location = _default_loader.location
