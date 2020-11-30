import bpy
from bpy.utils import register_class, unregister_class
from . import scene, object, atlas
from . renderer import cycles, luxcorerender
from . denoiser import oidn, optix

classes = [
    scene.TLM_SceneProperties,
    object.TLM_ObjectProperties,
    cycles.TLM_CyclesSceneProperties,
    luxcorerender.TLM_LuxCoreSceneProperties,
    oidn.TLM_OIDNEngineProperties,
    optix.TLM_OptixEngineProperties,
    atlas.TLM_AtlasListItem,
    atlas.TLM_UL_AtlasList,
    atlas.TLM_PostAtlasListItem,
    atlas.TLM_UL_PostAtlasList
]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.TLM_SceneProperties = bpy.props.PointerProperty(type=scene.TLM_SceneProperties)
    bpy.types.Object.TLM_ObjectProperties = bpy.props.PointerProperty(type=object.TLM_ObjectProperties)
    bpy.types.Scene.TLM_EngineProperties = bpy.props.PointerProperty(type=cycles.TLM_CyclesSceneProperties)
    bpy.types.Scene.TLM_Engine2Properties = bpy.props.PointerProperty(type=luxcorerender.TLM_LuxCoreSceneProperties)
    bpy.types.Scene.TLM_OIDNEngineProperties = bpy.props.PointerProperty(type=oidn.TLM_OIDNEngineProperties)
    bpy.types.Scene.TLM_OptixEngineProperties = bpy.props.PointerProperty(type=optix.TLM_OptixEngineProperties)
    bpy.types.Scene.TLM_AtlasListItem = bpy.props.IntProperty(name="Index for my_list", default=0)
    bpy.types.Scene.TLM_AtlasList = bpy.props.CollectionProperty(type=atlas.TLM_AtlasListItem)
    bpy.types.Scene.TLM_PostAtlasListItem = bpy.props.IntProperty(name="Index for my_list", default=0)
    bpy.types.Scene.TLM_PostAtlasList = bpy.props.CollectionProperty(type=atlas.TLM_PostAtlasListItem)

    bpy.types.Material.TLM_ignore = bpy.props.BoolProperty(name="Skip material", description="Ignore material for lightmapped object", default=False)

def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.TLM_SceneProperties
    del bpy.types.Object.TLM_ObjectProperties
    del bpy.types.Scene.TLM_EngineProperties
    del bpy.types.Scene.TLM_Engine2Properties
    del bpy.types.Scene.TLM_OIDNEngineProperties
    del bpy.types.Scene.TLM_OptixEngineProperties
    del bpy.types.Scene.TLM_AtlasListItem
    del bpy.types.Scene.TLM_AtlasList
    del bpy.types.Scene.TLM_PostAtlasListItem
    del bpy.types.Scene.TLM_PostAtlasList