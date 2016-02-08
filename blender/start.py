import project
import nodes_logic
import nodes_pipeline
import nodes_world
import armory
import traits_animation
import traits_params
import traits
import props

def register():
    project.register()
    nodes_logic.register()
    nodes_pipeline.register()
    nodes_world.register()
    armory.register()
    traits_animation.register()
    traits_params.register()
    traits.register()
    props.register()

def unregister():
    project.unregister()
    nodes_logic.unregister()
    nodes_pipeline.unregister()
    nodes_world.unregister()
    armory.unregister()
    traits_animation.unregister()
    traits_params.unregister()
    traits.unregister()
    props.unregister()
