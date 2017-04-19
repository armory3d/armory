import arm.nodes_logic
import arm.nodes_renderpath
import arm.make_renderer
import arm.props_traits_action
import arm.props_traits_clip
import arm.props_traits_library
import arm.props_traits_params
import arm.props_traits
import arm.props_lod
import arm.props_navigation
import arm.props_globalvars
import arm.props_virtualinput
import arm.props
import arm.props_ui
import arm.props_renderer
import arm.handlers
import arm.space_armory
import arm.utils
import arm.keymap

registered = False

def register():
    global registered
    registered = True
    arm.utils.register()
    arm.props_traits_action.register()
    arm.props_traits_clip.register()
    arm.props_traits_library.register()
    arm.props.register()
    arm.props_ui.register()
    arm.props_renderer.register()
    arm.nodes_logic.register()
    arm.nodes_renderpath.register()
    arm.make_renderer.register()
    arm.props_traits_params.register()
    arm.props_traits.register()
    arm.props_lod.register()
    arm.props_navigation.register()
    arm.props_globalvars.register()
    arm.props_virtualinput.register()
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
    arm.props_traits_params.unregister()
    arm.props_traits.unregister()
    arm.props_lod.unregister()
    arm.props_navigation.unregister()
    arm.props_globalvars.unregister()
    arm.props_virtualinput.unregister()
    arm.handlers.unregister()
    arm.props_renderer.unregister()
    arm.props_ui.unregister()
    arm.props.unregister()
    arm.props_traits_action.unregister()
    arm.props_traits_clip.unregister()
    arm.props_traits_library.unregister()
    arm.space_armory.unregister()
