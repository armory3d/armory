import project
import nodes
import scene
import traits_animation
import traits
import props

def register():
    project.register()
    nodes.register()
    scene.register()
    traits_animation.register()
    traits.register()
    props.register()

def unregister():
    project.unregister()
    nodes.unregister()
    scene.unregister()
    traits_animation.unregister()
    traits.unregister()
    props.unregister()
