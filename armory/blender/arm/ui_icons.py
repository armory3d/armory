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

_ICONS_DICT: Optional[bpy.utils.previews.ImagePreviewCollection] = None
"""Dictionary of all loaded icons, or `None` if not loaded"""

_ICONS_DIR = os.path.join(os.path.dirname(__file__), "custom_icons")
"""Directory of the icon files"""


def _load_icons():
    """(Re)loads all icons."""
    global _ICONS_DICT

    _unload_icons()

    _ICONS_DICT = bpy.utils.previews.new()
    _ICONS_DICT.load("bundle", os.path.join(_ICONS_DIR, "bundle.png"), 'IMAGE', force_reload=True)
    _ICONS_DICT.load("haxe", os.path.join(_ICONS_DIR, "haxe.png"), 'IMAGE', force_reload=True)
    _ICONS_DICT.load("wasm", os.path.join(_ICONS_DIR, "wasm.png"), 'IMAGE', force_reload=True)


def _unload_icons():
    """Unloads all icons."""
    global _ICONS_DICT
    if _ICONS_DICT is not None:
        bpy.utils.previews.remove(_ICONS_DICT)
    _ICONS_DICT = None


def get_id(identifier: str) -> int:
    """Returns the icon ID from the given identifier."""
    if _ICONS_DICT is None:
        _load_icons()
    return _ICONS_DICT[identifier].icon_id
