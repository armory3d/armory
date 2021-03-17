import bpy
from bpy.props import *
from bpy.types import Panel

class ARM_PT_RbCollisionFilterMaskPanel(bpy.types.Panel):
    bl_label = "Collections Filter Mask"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_parent_id = "ARM_PT_PhysicsPropsPanel"

    @classmethod
    def poll(self, context):
        obj = context.object
        if obj is None:
            return False
        return obj.rigid_body is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        obj = context.object
        layout.prop(obj, 'arm_rb_collision_filter_mask', text="", expand=True)

def register():
    bpy.utils.register_class(ARM_PT_RbCollisionFilterMaskPanel)

def unregister():
    bpy.utils.unregister_class(ARM_PT_RbCollisionFilterMaskPanel)
