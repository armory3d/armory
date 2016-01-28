import project
import nodes
import pipeline_nodes
import armory
import traits_animation
import traits_params
import traits
import props

def register():
    project.register()
    nodes.register()
    pipeline_nodes.register()
    armory.register()
    traits_animation.register()
    traits_params.register()
    traits.register()
    props.register()

def unregister():
    project.unregister()
    nodes.unregister()
    pipeline_nodes.unregister()
    armory.unregister()
    traits_animation.unregister()
    traits_params.unregister()
    traits.unregister()
    props.unregister()
