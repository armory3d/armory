import bpy
from bpy.props import *

class TLM_ObjectProperties(bpy.types.PropertyGroup):
    tlm_image_scale_method : EnumProperty(
        items = [('Native', 'Native', 'TODO'),
                 ('OpenCV', 'OpenCV', 'TODO')],
                name = "Scaling engine", 
                description="TODO", 
                default='Native')