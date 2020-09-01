import os
import bpy

from bpy.utils import previews

icons = None
directory = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'icons'))

def id(identifier):
    return image(identifier).icon_id

def image(identifier):
    def icon(identifier):
        if identifier in icons:
            return icons[identifier]
        return icons.load(identifier, os.path.join(directory, identifier + '.png'), 'IMAGE')

    if icons:
        return icon(identifier)
    else:
        create()
        return icon(identifier)


def create():
    global icons
    icons = previews.new()


def remove():
    previews.remove(icons)