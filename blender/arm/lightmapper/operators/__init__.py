import bpy
from bpy.utils import register_class, unregister_class
from . import tlm, installopencv

classes = [
    tlm.TLM_BuildLightmaps,
    tlm.TLM_CleanLightmaps,
    tlm.TLM_ExploreLightmaps,
    tlm.TLM_EnableSelection,
    tlm.TLM_DisableSelection,
    tlm.TLM_RemoveLightmapUV,
    installopencv.TLM_Install_OpenCV
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)