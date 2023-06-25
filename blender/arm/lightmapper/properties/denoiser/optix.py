import bpy
from bpy.props import *

class TLM_OptixEngineProperties(bpy.types.PropertyGroup):

    tlm_optix_path : StringProperty(
        name="Optix Path", 
        description="TODO", 
        default="", 
        subtype="FILE_PATH")

    tlm_optix_verbose : BoolProperty(
        name="Verbose", 
        description="TODO")

    tlm_optix_maxmem : IntProperty(
            name="Tiling max Memory", 
            default=0, 
            min=512, 
            max=32768, 
            description="Use tiling for memory conservation. Set to 0 to disable tiling.")