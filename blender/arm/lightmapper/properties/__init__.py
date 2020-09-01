import bpy
from bpy.utils import register_class, unregister_class
from . import scene, object
from . renderer import cycles
from . denoiser import oidn, optix

classes = [
    scene.TLM_SceneProperties,
    object.TLM_ObjectProperties,
    cycles.TLM_CyclesSceneProperties,
    oidn.TLM_OIDNEngineProperties,
    optix.TLM_OptixEngineProperties
]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.TLM_SceneProperties = bpy.props.PointerProperty(type=scene.TLM_SceneProperties)
    bpy.types.Object.TLM_ObjectProperties = bpy.props.PointerProperty(type=object.TLM_ObjectProperties)
    bpy.types.Scene.TLM_EngineProperties = bpy.props.PointerProperty(type=cycles.TLM_CyclesSceneProperties)
    bpy.types.Scene.TLM_OIDNEngineProperties = bpy.props.PointerProperty(type=oidn.TLM_OIDNEngineProperties)
    bpy.types.Scene.TLM_OptixEngineProperties = bpy.props.PointerProperty(type=optix.TLM_OptixEngineProperties)

def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.TLM_SceneProperties
    del bpy.types.Object.TLM_ObjectProperties
    del bpy.types.Scene.TLM_EngineProperties
    del bpy.types.Scene.TLM_OIDNEngineProperties
    del bpy.types.Scene.TLM_OptixEngineProperties