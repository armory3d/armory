import arm.nodes_logic
import arm.nodes_renderpath
import arm.make_renderer
import arm.props_traits_params
import arm.props_traits_props
import arm.props_traits
import arm.props_lod
import arm.props_tilesheet
import arm.props_exporter
import arm.props_renderpath
import arm.props
import arm.props_ui
import arm.handlers
import arm.space_armory
import arm.utils
import arm.keymap

registered = False

def register():
    global registered
    registered = True
    arm.utils.register()
    arm.props_traits_params.register()
    arm.props_traits_props.register()
    arm.props_traits.register()
    arm.props_lod.register()
    arm.props_tilesheet.register()
    arm.props_exporter.register()
    arm.props_renderpath.register()
    arm.props.register()
    arm.props_ui.register()
    arm.nodes_logic.register()
    arm.nodes_renderpath.register()
    arm.make_renderer.register()
    arm.space_armory.register()
    arm.keymap.register()
    arm.handlers.register()

def unregister():
    global registered
    registered = False
    arm.keymap.unregister()
    arm.utils.unregister()
    arm.nodes_logic.unregister()
    arm.make_renderer.unregister()
    arm.nodes_renderpath.unregister()
    arm.handlers.unregister()
    arm.props_ui.unregister()
    arm.props.unregister()
    arm.props_traits_params.unregister()
    arm.props_traits_props.unregister()
    arm.props_traits.unregister()
    arm.props_lod.unregister()
    arm.props_tilesheet.unregister()
    arm.props_exporter.unregister()
    arm.props_renderpath.unregister()
    arm.space_armory.unregister()
