import bpy


class ARM_PT_RbCollisionFilterMaskPanel(bpy.types.Panel):
    bl_label = "Armory Collision Filter Mask"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        obj = bpy.context.object
        if obj is None:
            return
        if obj.rigid_body is not None:
            layout.prop(obj, 'arm_rb_collision_filter_mask')


def register():
    bpy.utils.register_class(ARM_PT_RbCollisionFilterMaskPanel)
    bpy.types.Object.arm_rb_collision_filter_mask = bpy.props.BoolVectorProperty(
        name="Collision Filter Mask",
        default=[True] + [False] * 19,
        size=20,
        subtype='LAYER')


def unregister():
    bpy.utils.unregister_class(ARM_PT_RbCollisionFilterMaskPanel)
