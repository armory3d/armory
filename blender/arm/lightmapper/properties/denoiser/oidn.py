import bpy
from bpy.props import *

class TLM_OIDNEngineProperties(bpy.types.PropertyGroup):
    tlm_oidn_path : StringProperty(
        name="OIDN Path", 
        description="The path to the OIDN binaries", 
        default="", 
        subtype="FILE_PATH")

    tlm_oidn_verbose : BoolProperty(
        name="Verbose", 
        description="TODO")

    tlm_oidn_threads : IntProperty(
        name="Threads", 
        default=0, 
        min=0, 
        max=64, 
        description="Amount of threads to use. Set to 0 for auto-detect.")

    tlm_oidn_maxmem : IntProperty(
        name="Tiling max Memory", 
        default=0, 
        min=512, 
        max=32768, 
        description="Use tiling for memory conservation. Set to 0 to disable tiling.")

    tlm_oidn_affinity : BoolProperty(
        name="Set Affinity", 
        description="TODO")

    tlm_oidn_use_albedo : BoolProperty(
        name="Use albedo map", 
        description="TODO")

    tlm_oidn_use_normal : BoolProperty(
        name="Use normal map", 
        description="TODO")