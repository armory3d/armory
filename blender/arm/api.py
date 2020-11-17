from typing import Callable, Dict, Optional

from bpy.types import UILayout

from arm.material.shader import ShaderContext

drivers: Dict[str, Dict] = dict()


def add_driver(driver_name: str,
               draw_props: Callable[[UILayout], None],
               make_rpass: Callable[[str], Optional[ShaderContext]], make_rpath: Callable[[], None]) -> None:
    """Register a new driver. If there already exists a driver with the given name, nothing happens.

    @param driver_name Unique name for the new driver
    @param draw_props Function to draw global driver properties inside the render path panel
    @param make_rpass Function to create render passes. Takes the rpass name as a parameter and may return `None`.
    @param make_rpath Function to setup the render path.
    """
    global drivers

    if driver_name in drivers:
        return

    drivers[driver_name] = {
        'driver_name': driver_name,
        'draw_props': draw_props,
        'make_rpass': make_rpass,
        'make_rpath': make_rpath
    }
