import bpy
from bpy.props import *

class TLM_LuxCoreSceneProperties(bpy.types.PropertyGroup):

    #Luxcore specific here
    tlm_luxcore_dir : StringProperty(
        name="Luxcore Directory", 
        description="Standalone path to your LuxCoreRender binary.", 
        default="", 
        subtype="FILE_PATH")