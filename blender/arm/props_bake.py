import os
import shutil
import arm.assets as assets
import arm.utils
import bpy
import stat
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmBakeListItem(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")

class ArmBakeList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "object_name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class ArmBakeListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_bakelist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        scn = context.scene
        scn.arm_bakelist.add()
        scn.arm_bakelist_index = len(scn.arm_bakelist) - 1
        return{'FINISHED'}


class ArmBakeListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_bakelist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        scn = context.scene
        return len(scn.arm_bakelist) > 0

    def execute(self, context):
        scn = context.scene
        list = scn.arm_bakelist
        index = scn.arm_bakelist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        scn.arm_bakelist_index = index
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmBakeListItem)
    bpy.utils.register_class(ArmBakeList)
    bpy.utils.register_class(ArmBakeListNewItem)
    bpy.utils.register_class(ArmBakeListDeleteItem)
    bpy.types.Scene.arm_bakelist = bpy.props.CollectionProperty(type=ArmBakeListItem)
    bpy.types.Scene.arm_bakelist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

def unregister():
    bpy.utils.unregister_class(ArmBakeListItem)
    bpy.utils.unregister_class(ArmBakeList)
    bpy.utils.unregister_class(ArmBakeListNewItem)
    bpy.utils.unregister_class(ArmBakeListDeleteItem)
