import bpy
from bpy.props import *

class TLM_OctanerenderSceneProperties(bpy.types.PropertyGroup):

    tlm_lightmap_savedir : StringProperty(
        name="Lightmap Directory", 
        description="TODO", 
        default="Lightmaps", 
        subtype="FILE_PATH")