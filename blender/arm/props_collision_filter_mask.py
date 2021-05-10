import bpy


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
        layout.use_property_split = False
        layout.use_property_decorate = False
        obj = context.object
        layout.prop(obj, 'arm_rb_collision_filter_mask', text="", expand=True)
        col_mask = ''
        for b in obj.arm_rb_collision_filter_mask:
            col_mask = ('1' if b else '0') + col_mask
        col = layout.column()
        row = col.row()
        row.alignment = 'RIGHT'
        row.label(text=f'Integer Mask Value: {str(int(col_mask, 2))}')


def register():
    bpy.utils.register_class(ARM_PT_RbCollisionFilterMaskPanel)


def unregister():
    bpy.utils.unregister_class(ARM_PT_RbCollisionFilterMaskPanel)
