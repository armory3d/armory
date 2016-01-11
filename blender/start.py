import project
import nodes
import armory
import traits_animation
import traits
import props

def register():
    project.register()
    nodes.register()
    armory.register()
    traits_animation.register()
    traits.register()
    props.register()

def unregister():
    project.unregister()
    nodes.unregister()
    armory.unregister()
    traits_animation.unregister()
    traits.unregister()
    props.unregister()
