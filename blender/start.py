import arm.nodes_logic
import arm.props_traits_props
import arm.props_traits
import arm.props_lod
import arm.props_tilesheet
import arm.props_exporter
import arm.props_bake
import arm.props_renderpath
import arm.props_properties
import arm.props
import arm.props_ui
import arm.handlers
import arm.utils
import arm.keymap

registered = False

def register(local_sdk=False):
    global registered
    registered = True
    arm.utils.register(local_sdk=local_sdk)
    arm.props_traits_props.register()
    arm.props_traits.register()
    arm.props_lod.register()
    arm.props_tilesheet.register()
    arm.props_exporter.register()
    arm.props_bake.register()
    arm.props_renderpath.register()
    arm.props_properties.register()
    arm.props.register()
    arm.props_ui.register()
    arm.nodes_logic.register()
    arm.keymap.register()
    arm.handlers.register()

def unregister():
    global registered
    registered = False
    arm.keymap.unregister()
    arm.utils.unregister()
    arm.nodes_logic.unregister()
    arm.handlers.unregister()
    arm.props_ui.unregister()
    arm.props.unregister()
    arm.props_traits_props.unregister()
    arm.props_traits.unregister()
    arm.props_lod.unregister()
    arm.props_tilesheet.unregister()
    arm.props_exporter.unregister()
    arm.props_bake.unregister()
    arm.props_renderpath.unregister()
    arm.props_properties.unregister()
