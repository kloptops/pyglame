# ----------------------------------------------------------------------------
#
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
#  * Neither the name of pyglame nor the names of its
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

import json
import os
import re

import pygame
import pyglame

from pyglame import surface

def default_name_fixer(file_name, duplicate=False):
    new_name = file_name.rsplit('/',1)[-1]
    if duplicate:
        temp = new_name.rsplit('.',1)
        new_name = "{}_{:03d}.{}".format(temp[0], duplicate, temp[1])
    return new_name

def atlases_add(atlases, image, width, height):
    for i, atlas in enumerate(atlases):
        try:
            return i, atlas.add(image)
        except surface.atlas.AllocatorException:
            pass
    else:
        atlas = surface.atlas.SurfaceAtlas(width, height)
        atlases.append(atlas)
        return len(atlases)-1, atlas.add(image)


def bake_atlas(
        out_folder, atlas_name,
        file_info,
        width, height,
        name_fixer=default_name_fixer):

    atlases = []
    images  = {}
    new_names = {}

    for file_location, old_file_name in file_info:
        image = surface.load(old_file_name, file_location.open(old_file_name))
        file_name = name_fixer(old_file_name, False)

        i = 1
        while file_name in images:
            file_name = name_fixer(old_file_name, i)
            i += 1

        if image.width > (width/2) or image.height > (height/2):
            new_names[old_file_name] = None
            print "Skipping {} ({} x {}), image too big.".format(
                file_name, image.width, image.height)
            continue

        new_names[old_file_name] = file_name

        images[file_name] = image

    output = {'Version': '0.1', 'Images': {}, "Atlases": []}
    for file_name, image in sorted(
            images.items(),
            key=lambda (x, y): (-y.height, -y.width, x)):
        atlas_id, image = atlases_add(atlases, image, width, height)

        output['Images'][file_name] = [
            "{}_{:03d}.png".format(atlas_name, atlas_id),
            image.x, image.y, image.width, image.height]

    packed = 0
    for i, atlas in enumerate(atlases):
        atlas_image_name = "{}_{:03d}.png".format(atlas_name, i)
        pygame.image.save(atlas.surface.surface, os.path.join(out_folder, atlas_image_name))
        output['Atlases'].append(atlas_image_name)
        packed += atlas.allocator.get_fragmentation()

    ## Nicer json formatting :D
    def fix_arrays(x):
        temp = json.dumps(json.loads(x.group(1)))
        temp = re.sub(r', (\d+)', lambda y: ", {:4d}".format(int(y.group(1))), temp)
        return temp

    temp = json.dumps(output, sort_keys=True, indent=4)
    temp = re.sub(r'(\[(?:\s*(?:(?:".*?"|\d+),?))+\s*?\])', fix_arrays, temp)

    atlas_file_name = os.path.join(out_folder, "{}.json".format(atlas_name))
    with open(atlas_file_name, 'w') as file_handle:
        file_handle.write(temp)

    return atlas_file_name, new_names

