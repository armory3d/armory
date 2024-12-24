from typing import Callable, Dict, Optional

import bpy
from bpy.types import Material, UILayout

import arm
from arm.material.shader import ShaderContext

if arm.is_reload(__name__):
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import ShaderContext
else:
    drivers: Dict[str, Dict] = {} #dict()

    arm.enable_reload(__name__)


def add_driver(driver_name: str,
               make_rpass: Callable[[str], Optional[ShaderContext]],
               make_rpath: Callable[[], None],
               draw_props: Optional[Callable[[UILayout], None]],
               draw_mat_props: Optional[Callable[[UILayout, Material], None]]) -> None:
    """Register a new driver. If there already exists a driver with the given name, nothing happens.

    @param driver_name Unique name for the new driver that will be displayed in the UI.
    @param make_rpass Function to create render passes. Takes the rpass name as a parameter and may return `None`.
    @param make_rpath Function to setup the render path.
    @param draw_props Function to draw global driver properties inside the render path panel, may be `None`.
    @param draw_mat_props Function to draw per-material driver properties in the material tab, may be `None`.
    """
    global drivers

    if driver_name in drivers:
        return

    drivers[driver_name] = {
        'driver_name': driver_name,
        'make_rpass': make_rpass,
        'make_rpath': make_rpath,
        'draw_props': draw_props,
        'draw_mat_props': draw_mat_props
    }

    wrd = bpy.data.worlds['Arm']
    if len(wrd.rp_driver_list) == 0:
        wrd.rp_driver_list.add().name = 'Armory' # Add default driver
    wrd.rp_driver_list.add().name = driver_name


def remove_drivers():
    wrd = bpy.data.worlds['Arm']
    wrd.rp_driver_list.clear()
    wrd.rp_driver_list.add().name = 'Armory'

    drivers.clear()
