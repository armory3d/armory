import time

import arm
import arm.log
import arm.nodes_logic
import arm.nodes_material
import arm.props_traits_props
import arm.props_traits
import arm.props_lod
import arm.props_action
import arm.props_tilesheet
import arm.props_exporter
import arm.props_bake
import arm.props_renderpath
import arm.props_properties
import arm.props_collision_filter_mask
import arm.props
import arm.props_ui
import arm.handlers
import arm.utils
import arm.keymap

reload_started = 0

if arm.is_reload(__name__):
    arm.log.debug('Reloading Armory SDK...')
    reload_started = time.time()

    # Clear the module cache
    import importlib
    arm = importlib.reload(arm)  # type: ignore

    arm.nodes_logic = arm.reload_module(arm.nodes_logic)
    arm.nodes_material = arm.reload_module(arm.nodes_material)
    arm.props_traits_props = arm.reload_module(arm.props_traits_props)
    arm.props_traits = arm.reload_module(arm.props_traits)
    arm.props_lod = arm.reload_module(arm.props_lod)
    arm.props_action = arm.reload_module(arm.props_action)
    arm.props_tilesheet = arm.reload_module(arm.props_tilesheet)
    arm.props_exporter = arm.reload_module(arm.props_exporter)
    arm.props_bake = arm.reload_module(arm.props_bake)
    arm.props_renderpath = arm.reload_module(arm.props_renderpath)
    arm.props_properties = arm.reload_module(arm.props_properties)
    arm.props_collision_filter_mask = arm.reload_module(arm.props_collision_filter_mask)
    arm.props = arm.reload_module(arm.props)
    arm.props_ui = arm.reload_module(arm.props_ui)
    arm.handlers = arm.reload_module(arm.handlers)
    arm.utils = arm.reload_module(arm.utils)
    arm.keymap = arm.reload_module(arm.keymap)
else:
    arm.enable_reload(__name__)

registered = False


def register(local_sdk=False):
    global registered
    registered = True
    arm.utils.register(local_sdk=local_sdk)
    arm.props_traits_props.register()
    arm.props_traits.register()
    arm.props_lod.register()
    arm.props_action.register()
    arm.props_tilesheet.register()
    arm.props_exporter.register()
    arm.props_bake.register()
    arm.props_renderpath.register()
    arm.props_properties.register()
    arm.props.register()
    arm.props_ui.register()
    arm.nodes_logic.register()
    arm.nodes_material.register()
    arm.keymap.register()
    arm.handlers.register()
    arm.props_collision_filter_mask.register()

    arm.handlers.post_register()

    if reload_started != 0:
        arm.log.debug(f'Armory SDK: Reloading finished in {time.time() - reload_started:.3f}s')


def unregister():
    global registered
    registered = False
    arm.keymap.unregister()
    arm.utils.unregister()
    arm.nodes_material.unregister()
    arm.nodes_logic.unregister()
    arm.handlers.unregister()
    arm.props_ui.unregister()
    arm.props.unregister()
    arm.props_traits_props.unregister()
    arm.props_traits.unregister()
    arm.props_action.unregister()
    arm.props_lod.unregister()
    arm.props_tilesheet.unregister()
    arm.props_exporter.unregister()
    arm.props_bake.unregister()
    arm.props_renderpath.unregister()
    arm.props_properties.unregister()
    arm.props_collision_filter_mask.unregister()
