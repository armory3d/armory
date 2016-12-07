import make
import nodes_logic
import nodes_renderpath
import props_traits_action
import props_traits_clip
import props_traits_params
import props_traits
import props_lod
import props_navigation
import props
import props_ui
import gen_renderpath
import handlers
import space_armory
import armutils
import keymap

def register():
    armutils.register()
    props_traits_action.register()
    props_traits_clip.register()
    props.register()
    props_ui.register()
    gen_renderpath.register()
    handlers.register()
    nodes_logic.register()
    nodes_renderpath.register()
    props_traits_params.register()
    props_traits.register()
    props_lod.register()
    props_navigation.register()
    space_armory.register()
    keymap.register()

def unregister():
    keymap.unregister()
    armutils.unregister()
    nodes_logic.unregister()
    nodes_renderpath.unregister()
    props_traits_params.unregister()
    props_traits.unregister()
    props_lod.unregister()
    props_navigation.unregister()
    handlers.unregister()
    gen_renderpath.unregister()
    props_ui.unregister()
    props.unregister()
    props_traits_action.unregister()
    props_traits_clip.unregister()
    space_armory.unregister()
