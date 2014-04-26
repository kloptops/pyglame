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

'''Image load, capture and high-level texture functions.

Only basic functionality is described here; for full reference see the
accompanying documentation.

To load an image::

    from pyglet import image
    pic = image.load('picture.png')

The supported image file types include PNG, BMP, GIF, JPG, and many more,
somewhat depending on the operating system.  To load an image from a file-like
object instead of a filename::

    pic = image.load('hint.jpg', file=fileobj)

The hint helps the module locate an appropriate decoder to use based on the
file extension.  It is optional.

Once loaded, images can be used directly by most other modules of pyglet.  All
images have a width and height you can access::

    width, height = pic.width, pic.height

You can extract a region of an image (this keeps the original image intact;
the memory is shared efficiently)::

    subimage = pic.get_region(x, y, width, height)

Remember that y-coordinates are always increasing upwards.

Drawing images
--------------

To draw an image at some point on the screen::

    pic.blit(x, y, z)

This assumes an appropriate view transform and projection have been applied.

Some images have an intrinsic "anchor point": this is the point which will be
aligned to the ``x`` and ``y`` coordinates when the image is drawn.  By
default the anchor point is the lower-left corner of the image.  You can use
the anchor point to center an image at a given point, for example::

    pic.anchor_x = pic.width // 2
    pic.anchor_y = pic.height // 2
    pic.blit(x, y, z)

Texture access
--------------

If you are using OpenGL directly, you can access the image as a texture::

    texture = pic.get_texture()

(This is the most efficient way to obtain a texture; some images are
immediately loaded as textures, whereas others go through an intermediate
form).  To use a texture with pyglet.gl::

    from pyglet.gl import *
    glEnable(texture.target)        # typically target is GL_TEXTURE_2D
    glBindTexture(texture.target, texture.id)
    # ... draw with the texture

Pixel access
------------

To access raw pixel data of an image::

    rawimage = pic.get_image_data()

(If the image has just been loaded this will be a very quick operation;
however if the image is a texture a relatively expensive readback operation
will occur).  The pixels can be accessed as a string::

    format = 'RGBA'
    pitch = rawimage.width * len(format)
    pixels = rawimage.get_data(format, pitch)

"format" strings consist of characters that give the byte order of each color
component.  For example, if rawimage.format is 'RGBA', there are four color
components: red, green, blue and alpha, in that order.  Other common format
strings are 'RGB', 'LA' (luminance, alpha) and 'I' (intensity).

The "pitch" of an image is the number of bytes in a row (this may validly be
more than the number required to make up the width of the image, it is common
to see this for word alignment).  If "pitch" is negative the rows of the image
are ordered from top to bottom, otherwise they are ordered from bottom to top.

Retrieving data with the format and pitch given in `ImageData.format` and
`ImageData.pitch` avoids the need for data conversion (assuming you can make
use of the data in this arbitrary format).

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: __init__.py 2541 2009-12-31 04:31:11Z benjamin.coder.smith@gmail.com $'

import sys
import re
import warnings
import weakref

from ctypes import *
from math import ceil
from StringIO import StringIO

from pyglame.window import *
from pyglame import draw
from pyglame.image import atlas

import pygame

class ImageException(Exception):
    pass

def load(filename, file=None):
    '''Load an image from a file.

    :note: You can make no assumptions about the return type; usually it will
        be ImageData or CompressedImageData, but decoders are free to return
        any subclass of AbstractImage.

    :Parameters:
        `filename` : str
            Used to guess the image format, and to load the file if `file` is
            unspecified.
        `file` : file-like object or None
            Source of image data in any supported format.
        `decoder` : ImageDecoder or None
            If unspecified, all decoders that are registered for the filename
            extension are tried.  If none succeed, the exception from the
            first decoder is raised.

    :rtype: AbstractImage
    '''

    if not file:
        file = open(filename, 'rb')
    if not hasattr(file, 'seek'):
        file = StringIO(file.read())

    surface = pygame.image.load(file, filename)

    return ImageSurface(
        surface.get_width(), surface.get_height(), surface)


class AbstractImage(object):
    '''Abstract class representing an image.

    :Ivariables:
        `width` : int
            Width of image
        `height` : int
            Height of image
        `anchor_x` : int
            X coordinate of anchor, relative to left edge of image data
        `anchor_y` : int
            Y coordinate of anchor, relative to top edge of image data
    '''
    anchor_x = 0
    anchor_y = 0

    _is_rectangle = False

    def __init__(self, width, height):
        self.width  = width
        self.height = height

    def __repr__(self):
        return '<%s %dx%d>' % (self.__class__.__name__, self.width, self.height)

    def get_surface(self):
        '''Get a pygame.Surface of this image.

        Changes to the returned instance may or may not be reflected in this
        image.

        :rtype: `pygame.Surface`

        :since: pyglame 0.0.1
        '''
        raise ImageException('Cannot retrieve image data for %r' % self)

    surface = property(lambda self: self.get_surface(),
        doc=''' a pygame.Surface of this image.

        Changes to the returned instance may or may not be reflected in this
        image. Read-only.

        :since: pyglame 0.0.1

        :type: `pygame.Surface`
        ''')

    def get_region(self, x, y, width, height):
        '''Retrieve a rectangular region of this image.

        :Parameters:
            `x` : int
                Left edge of region.
            `y` : int
                Bottom edge of region.
            `width` : int
                Width of region.
            `height` : int
                Height of region.

        :rtype: AbstractImage
        '''
        raise ImageException('Cannot get region for %r' % self)

    def save(self, filename):
        '''Save this image to a file.

        :Parameters:
            `filename` : str
                Used to set the image file format, and to open the output file
                if `file` is unspecified.
        '''
        pygame.image.save(self.surface, filename)

    def blit_into(self, surface, x, y, area=None):
        '''Draw `source` on this image.

        `source` will be copied into this image such that its anchor point
        is aligned with the `x` and `y` parameters.  If this image is a 3D
        texture, the `z` coordinate gives the image slice to copy into.

        Note that if `source` is larger than this image (or the positioning
        would cause the copy to go out of bounds) then you must pass a
        region of `source` to this method, typically using get_region().
        '''
        raise ImageException('Cannot blit images onto %r.' % self)


def _nearest_pow2(v):
    # From http://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    # Credit: Sean Anderson
    v -= 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    return v + 1

def _is_pow2(v):
    # http://graphics.stanford.edu/~seander/bithacks.html#DetermineIfPowerOf2
    return (v & (v - 1)) == 0


class ImageSurface(AbstractImage):

    def __init__(self, width, height, surface):
        super(ImageSurface, self).__init__(width, height)
        self._surface = surface

    @classmethod
    def create(cls, width, height, depth=32, rectangle=False):
        '''Create an empty Texture.

        If `rectangle` is ``False`` or the appropriate driver extensions are
        not available, a larger texture than requested will be created, and
        a `TextureRegion` corresponding to the requested size will be
        returned.

        :Parameters:
            `width` : int
                Width of the surface.
            `height` : int
                Height of the surface.
            `depth` : int
                Depth of surface.
            `pow2` : bool
                Ensure the surface sizes are a power of 2

        :rtype: `Texture`

        :since: pyglame 1.1
        '''

        if rectangle:
            width  = _nearest_pow2(width)
            height = _nearest_pow2(height)

        surface = pygame.Surface((width, height), 0, depth)

        image = cls(width, height, surface)
        image._is_rectangle = rectangle

    def get_surface(self):
        return self._surface

    def blit_into(self, im_surface, x, y, area=None):
        draw.blit_into(self, im_surface, x, y)

    def get_region(self, x, y, width, height):
        return ImageRegion(x, y, width, height, self)


class ImageRegion(ImageSurface):
    '''A rectangular region of a texture, presented as if it were
    a separate texture.
    '''

    def __init__(self, x, y, width, height, parent):
        self.parent = parent

        new_surface = parent.surface.subsurface((x, y, width, height))

        super(ImageRegion, self).__init__(
            width, height, new_surface)
