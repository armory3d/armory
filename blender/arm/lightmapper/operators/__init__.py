import bpy
from bpy.utils import register_class, unregister_class
from . import tlm, installopencv, imagetools

classes = [
    tlm.TLM_BuildLightmaps,
    tlm.TLM_CleanLightmaps,
    tlm.TLM_ExploreLightmaps,
    tlm.TLM_EnableSet,
    tlm.TLM_DisableSelection,
    tlm.TLM_RemoveLightmapUV,
    tlm.TLM_SelectLightmapped,
    tlm.TLM_ToggleTexelDensity,
    installopencv.TLM_Install_OpenCV,
    tlm.TLM_AtlasListNewItem,
    tlm.TLM_AtlastListDeleteItem,
    tlm.TLM_AtlasListMoveItem,
    tlm.TLM_PostAtlasListNewItem,
    tlm.TLM_PostAtlastListDeleteItem,
    tlm.TLM_PostAtlasListMoveItem,
    tlm.TLM_StartServer,
    tlm.TLM_BuildEnvironmentProbes,
    tlm.TLM_CleanBuildEnvironmentProbes,
    tlm.TLM_PrepareUVMaps,
    tlm.TLM_LoadLightmaps,
    imagetools.TLM_ImageUpscale,
    imagetools.TLM_ImageDownscale

]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)