"""Custom bpy property creators for logic nodes. Please be aware that
the code in this file is usually run once at registration and not for
each individual node instance when it is created.

The functions for creating typed properties wrap the private __haxe_prop
function to allow for IDE autocompletion.

Some default parameters in the signature of functions in this module are
mutable (common Python pitfall, be aware of this!), but because they
don't get accessed later it doesn't matter here and we keep it this way
for parity with the Blender API.
"""
from typing import Any, Callable, Sequence, Union

import sys
import bpy
from bpy.props import *

__all__ = [
    'HaxeBoolProperty',
    'HaxeBoolVectorProperty',
    'HaxeCollectionProperty',
    'HaxeEnumProperty',
    'HaxeFloatProperty',
    'HaxeFloatVectorProperty',
    'HaxeIntProperty',
    'HaxeIntVectorProperty',
    'HaxePointerProperty',
    'HaxeStringProperty',
    'RemoveHaxeProperty'
]


def __haxe_prop(prop_type: Callable, prop_name: str, *args, **kwargs) -> Any:
    """Declares a logic node property as a property that will be
    used ingame for a logic node."""
    update_callback: Callable = kwargs.get('update', None)
    if update_callback is None:
        def wrapper(self: bpy.types.Node, context: bpy.types.Context):
            self.on_prop_update(context, prop_name)
        kwargs['update'] = wrapper
    else:
        def wrapper(self: bpy.types.Node, context: bpy.types.Context):
            update_callback(self, context)
            self.on_prop_update(context, prop_name)
        kwargs['update'] = wrapper

    # Tags are not allowed on classes other than bpy.types.ID or
    # bpy.types.Bone, remove them here to prevent registration errors
    if 'tags' in kwargs:
        del kwargs['tags']

    return prop_type(*args, **kwargs)


def HaxeBoolProperty(
        prop_name: str,
        *,  # force passing further arguments as keywords, see PEP 3102
        name: str = "",
        description: str = "",
        default=False,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        update=None,
        get=None,
        set=None
) -> 'bpy.types.BoolProperty':
    """Declares a new BoolProperty that has a Haxe counterpart with the
    given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(BoolProperty, **locals())


def HaxeBoolVectorProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default: list = (False, False, False),
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        size: int = 3,
        update=None,
        get=None,
        set=None
) -> list['bpy.types.BoolProperty']:
    """Declares a new BoolVectorProperty that has a Haxe counterpart
    with the given prop_name (Python and Haxe names must be identical
    for now).
    """
    return __haxe_prop(BoolVectorProperty, **locals())


def HaxeCollectionProperty(
        prop_name: str,
        *,
        type=None,
        name: str = "",
        description: str = "",
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set()
) -> 'bpy.types.CollectionProperty':
    """Declares a new CollectionProperty that has a Haxe counterpart
    with the given prop_name (Python and Haxe names must be identical
    for now).
    """
    return __haxe_prop(CollectionProperty, **locals())


def HaxeEnumProperty(
        prop_name: str,
        *,
        items: Sequence,
        name: str = "",
        description: str = "",
        default: Union[str, set[str]] = None,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        update=None,
        get=None,
        set=None
) -> 'bpy.types.EnumProperty':
    """Declares a new EnumProperty that has a Haxe counterpart with the
    given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(EnumProperty, **locals())


def HaxeFloatProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default=0.0,
        min: float = -3.402823e+38,
        max: float = 3.402823e+38,
        soft_min: float = -3.402823e+38,
        soft_max: float = 3.402823e+38,
        step: int = 3,
        precision: int = 2,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        unit: str = 'NONE',
        update=None,
        get=None,
        set=None
) -> 'bpy.types.FloatProperty':
    """Declares a new FloatProperty that has a Haxe counterpart with the
    given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(FloatProperty, **locals())


def HaxeFloatVectorProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default: list = (0.0, 0.0, 0.0),
        min: float = sys.float_info.min,
        max: float = sys.float_info.max,
        soft_min: float = sys.float_info.min,
        soft_max: float = sys.float_info.max,
        step: int = 3,
        precision: int = 2,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        unit: str = 'NONE',
        size: int = 3,
        update=None,
        get=None,
        set=None
) -> list['bpy.types.FloatProperty']:
    """Declares a new FloatVectorProperty that has a Haxe counterpart
    with the given prop_name (Python and Haxe names must be identical
    for now).
    """
    return __haxe_prop(FloatVectorProperty, **locals())


def HaxeIntProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default=0,
        min: int = -2**31,
        max: int = 2**31 - 1,
        soft_min: int = -2**31,
        soft_max: int = 2**31 - 1,
        step: int = 1,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        update=None,
        get=None,
        set=None
) -> 'bpy.types.IntProperty':
    """Declares a new IntProperty that has a Haxe counterpart with the
    given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(IntProperty, **locals())


def HaxeIntVectorProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default: list = (0, 0, 0),
        min: int = -2**31,
        max: int = 2**31 - 1,
        soft_min: int = -2**31,
        soft_max: int = 2**31 - 1,
        step: int = 1,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        size: int = 3,
        update=None,
        get=None,
        set=None
) -> list['bpy.types.IntProperty']:
    """Declares a new IntVectorProperty that has a Haxe counterpart with
    the given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(IntVectorProperty, **locals())


def HaxePointerProperty(
        prop_name: str,
        *,
        type=None,
        name: str = "",
        description: str = "",
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        poll=None,
        update=None
) -> 'bpy.types.PointerProperty':
    """Declares a new PointerProperty that has a Haxe counterpart with
    the given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(PointerProperty, **locals())


def RemoveHaxeProperty(cls, attr: str):
    RemoveProperty(cls, attr)


def HaxeStringProperty(
        prop_name: str,
        *,
        name: str = "",
        description: str = "",
        default: str = "",
        maxlen: int = 0,
        options: set = {'ANIMATABLE'},
        override: set = set(),
        tags: set = set(),
        subtype: str = 'NONE',
        update=None,
        get=None,
        set=None
) -> 'bpy.types.StringProperty':
    """Declares a new StringProperty that has a Haxe counterpart with
    the given prop_name (Python and Haxe names must be identical for now).
    """
    return __haxe_prop(StringProperty, **locals())
