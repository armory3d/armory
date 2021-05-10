"""
Blender user interface icon handling.
"""
import os.path
from typing import Optional

import bpy.utils.previews

_icons_dict: Optional[bpy.utils.previews.ImagePreviewCollection] = None
"""Dictionary of all loaded icons, or `None` if not loaded"""

_icons_dir = os.path.join(os.path.dirname(__file__), "custom_icons")
"""Directory of the icon files"""


def _load_icons() -> None:
    """(Re)loads all icons"""
    global _icons_dict

    if _icons_dict is not None:
        bpy.utils.previews.remove(_icons_dict)

    _icons_dict = bpy.utils.previews.new()
    _icons_dict.load("bundle", os.path.join(_icons_dir, "bundle.png"), 'IMAGE')
    _icons_dict.load("haxe", os.path.join(_icons_dir, "haxe.png"), 'IMAGE')
    _icons_dict.load("wasm", os.path.join(_icons_dir, "wasm.png"), 'IMAGE')


def get_id(identifier: str) -> int:
    """Returns the icon ID from the given identifier"""
    if _icons_dict is None:
        _load_icons()
    return _icons_dict[identifier].icon_id
