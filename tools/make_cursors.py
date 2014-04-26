# ----------------------------------------------------------------------------
# pyglame
# Copyright (c) 2014 Jacob Smith
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

from PIL import Image
import os

def process_image(file_name):
    im = Image.open(file_name)

    color_map = {
        (  0,   0,   0, 255): ('X', 0),
        ( 64,  64,  64, 255): ('X', 1),

        (255, 255, 255, 255): ('.', 0),
        (192, 192, 192, 255): ('.', 1),

        (255,   0, 255, 255): ('o', 0),
        (  0, 255,   0, 255): ('o', 1),
        (  0,   0, 255, 255): (' ', 1),
        }

    if im.mode == 'P':
        im = im.convert('RGBA')

    width, height = im.size
    if width % 8:
        width  += 8 - (width  % 8)
    if height % 8:
        height += 8 - (height % 8)

    pix = im.load()
    output = [
        [' '] * width
        for i in range(height)]
    hot = 0, 0
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            pixel = pix[x, y]
            data = color_map.get(pixel, (' ', 0))
            output[y][x] = data[0]
            if data[1]:
                hot = x, y

    return (width, height), hot, tuple(map(lambda x: ''.join(x), output))

def dump_cursors(file_handle, cursors):
    print >> file_handle, "cursors = {"
    for cursor_name, values in sorted(cursors.items()):
        print >> file_handle, "    {!r}: ({!r}, {!r}, (".format(
            cursor_name, values[0], values[1])
        for line in values[2]:
            print >> file_handle, "        {!r},".format(line)
        print >> file_handle, "        )),\n"
    print >> file_handle, "    }"

def dump_file(file_name, cursors):
    with open(file_name, 'w') as file_handle:
        print >> file_handle, """
# ----------------------------------------------------------------------------
# pyglame
# Copyright (c) 2014 Jacob Smith
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
#
# Auto-generated by 'tools/make_cursors.py'
#
# ----------------------------------------------------------------------------
""".lstrip()
        dump_cursors(file_handle, cursors)


def parse_cursors(folder, out_file):
    cursors = {}
    for file_name in os.listdir(folder):
        if not (file_name.startswith('cursor_') and file_name.endswith('.png')):
            continue

        try:
            cursors[file_name[7:-4]] = process_image(
                os.path.join(folder, file_name))
        except Exception as err:
            print "Error processing {!r}: {}".format(file_name, err)

    dump_file(out_file, cursors)


parse_cursors(
    'resources', os.path.join('pyglame', 'window', 'pygame', 'cursors.py'))