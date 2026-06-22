import bpy
from bpy.props import *

class ARM_UL_CameraList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop_search(item, "arm_camera_object_ptr", bpy.data, "objects", text="", icon='VIEW_CAMERA')

class ARM_CameraListItem(bpy.types.PropertyGroup):
    arm_camera_object_ptr: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Camera Object",
        poll=lambda self, obj_to_check: obj_to_check.type == 'CAMERA' and \
                                     (bpy.context.object is None or \
                                      not hasattr(bpy.context.object, 'arm_camera_list') or \
                                      (obj_to_check.name not in [
                                          item.arm_camera_object_ptr.name
                                          for item in bpy.context.object.arm_camera_list
                                          if item.arm_camera_object_ptr and item != self
                                      ]))
    )

class ARM_PT_ArmoryCameraRenderFilter(bpy.types.Panel):
    bl_label = "Armory Camera Render Filter"
    bl_idname = "ARM_PT_ArmoryCameraRenderFilter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()

        col = row.column()
        col.template_list(
            "ARM_UL_CameraList",
            "",
            obj,
            "arm_camera_list",
            obj,
            "arm_active_camera_index",
            rows=5
        )

        col = row.column(align=True)
        col.operator("arm.add_camera", icon='ADD', text="")

        if obj.arm_camera_list and obj.arm_active_camera_index >= 0 and obj.arm_active_camera_index < len(obj.arm_camera_list):
            op_remove = col.operator("arm.remove_camera", icon='REMOVE', text="")
            op_remove.arm_index = obj.arm_active_camera_index

            op_up = col.operator("arm.move_camera", icon='TRIA_UP', text="")
            op_up.arm_index = obj.arm_active_camera_index
            op_up.direction = 'UP'

            op_down = col.operator("arm.move_camera", icon='TRIA_DOWN', text="")
            op_down.arm_index = obj.arm_active_camera_index
            op_down.direction = 'DOWN'

class ARM_OT_AddCamera(bpy.types.Operator):
    bl_idname = "arm.add_camera"
    bl_label = "Add Camera"

    def execute(self, context):
        obj = context.object
        
        new_item = obj.arm_camera_list.add()
        obj.arm_active_camera_index = len(obj.arm_camera_list) - 1
        
        return {'FINISHED'}

class ARM_OT_RemoveCamera(bpy.types.Operator):
    bl_idname = "arm.remove_camera"
    bl_label = "Remove Camera"

    arm_index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.object
        if self.arm_index < len(obj.arm_camera_list):
            obj.arm_camera_list.remove(self.arm_index)
            if obj.arm_active_camera_index >= len(obj.arm_camera_list):
                obj.arm_active_camera_index = len(obj.arm_camera_list) - 1
        return {'FINISHED'}

class ARM_OT_MoveCamera(bpy.types.Operator):
    bl_idname = "arm.move_camera"
    bl_label = "Move Camera"

    arm_index: bpy.props.IntProperty()
    direction: bpy.props.EnumProperty(
        items=[('UP', "Up", "Move camera up"),
               ('DOWN', "Down", "Move camera down")],
        default='UP'
    )

    def execute(self, context):
        obj = context.object
        camera_list = obj.arm_camera_list
        target_index = -1

        if self.direction == 'UP':
            if self.arm_index > 0:
                target_index = self.arm_index - 1
        elif self.direction == 'DOWN':
            if self.arm_index < len(camera_list) - 1:
                target_index = self.arm_index + 1

        if target_index != -1:
            camera_list.move(self.arm_index, target_index)
            obj.arm_active_camera_index = target_index
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ARM_UL_CameraList)
    bpy.utils.register_class(ARM_CameraListItem)
    bpy.utils.register_class(ARM_PT_ArmoryCameraRenderFilter)
    bpy.utils.register_class(ARM_OT_AddCamera)
    bpy.utils.register_class(ARM_OT_RemoveCamera)
    bpy.utils.register_class(ARM_OT_MoveCamera)
    
    bpy.types.Object.arm_camera_list = bpy.props.CollectionProperty(type=ARM_CameraListItem)
    bpy.types.Object.arm_active_camera_index = bpy.props.IntProperty(name="Active Camera Index", default=-1)

def unregister():
    bpy.utils.unregister_class(ARM_UL_CameraList)
    bpy.utils.unregister_class(ARM_CameraListItem)
    bpy.utils.unregister_class(ARM_PT_ArmoryCameraRenderFilter)
    bpy.utils.unregister_class(ARM_OT_AddCamera)
    bpy.utils.unregister_class(ARM_OT_RemoveCamera)
    bpy.utils.unregister_class(ARM_OT_MoveCamera)
    
    if hasattr(bpy.types.Object, "arm_camera_list"):
        del bpy.types.Object.arm_camera_list
    if hasattr(bpy.types.Object, "arm_active_camera_index"):
        del bpy.types.Object.arm_active_camera_index