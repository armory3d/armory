"""
Blender user interface icon handling.
"""
import os.path
from typing import Optional

import bpy.utils.previews

import arm

if arm.is_reload(__name__):
    # _unload_icons is not available in the module scope yet
    def __unload():
        _unload_icons()

    # Refresh icons after reload
    __unload()
else:
    arm.enable_reload(__name__)


__all__ = ["get_id"]

_icons_dict: Optional[bpy.utils.previews.ImagePreviewCollection] = None
"""Dictionary of all loaded icons, or `None` if not loaded"""

_icons_dir = os.path.join(os.path.dirname(__file__), "custom_icons")
"""Directory of the icon files"""


def _load_icons():
    """(Re)loads all icons."""
    global _icons_dict

    _unload_icons()

    _icons_dict = bpy.utils.previews.new()
    _icons_dict.load("bundle", os.path.join(_icons_dir, "bundle.png"), 'IMAGE', force_reload=True)
    _icons_dict.load("haxe", os.path.join(_icons_dir, "haxe.png"), 'IMAGE', force_reload=True)
    _icons_dict.load("wasm", os.path.join(_icons_dir, "wasm.png"), 'IMAGE', force_reload=True)


def _unload_icons():
    """Unloads all icons."""
    global _icons_dict
    if _icons_dict is not None:
        bpy.utils.previews.remove(_icons_dict)
    _icons_dict = None


def get_id(identifier: str) -> int:
    """Returns the icon ID from the given identifier."""
    if _icons_dict is None:
        _load_icons()
    return _icons_dict[identifier].icon_id
