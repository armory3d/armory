import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmTilesheetActionListItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    start_prop = bpy.props.IntProperty(
           name="Start",
           description="A name for this item",
           default=0)

    end_prop = bpy.props.IntProperty(
           name="End",
           description="A name for this item",
           default=0)

    loop_prop = bpy.props.BoolProperty(
           name="Loop",
           description="A name for this item",
           default=True)

class ArmTilesheetActionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmTilesheetActionListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_tilesheetactionlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        trait.arm_tilesheetactionlist.add()
        trait.arm_tilesheetactionlist_index = len(trait.arm_tilesheetactionlist) - 1
        return{'FINISHED'}

class ArmTilesheetActionListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_tilesheetactionlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        return len(trait.arm_tilesheetactionlist) > 0

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        list = trait.arm_tilesheetactionlist
        index = trait.arm_tilesheetactionlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        trait.arm_tilesheetactionlist_index = index
        return{'FINISHED'}

class ArmTilesheetActionListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_tilesheetactionlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        return len(trait.arm_tilesheetactionlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        index = trait.arm_tilesheetactionlist_index
        list_length = len(trait.arm_tilesheetactionlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        trait = wrd.arm_tilesheetlist[wrd.arm_tilesheetlist_index]
        list = trait.arm_tilesheetactionlist
        index = trait.arm_tilesheetactionlist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            #queue.move(index,neighbor)
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            #queue.move(neighbor, index)
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

class ArmTilesheetListItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    tilesx_prop = bpy.props.IntProperty(
           name="Tiles X",
           description="A name for this item",
           default=0)

    tilesy_prop = bpy.props.IntProperty(
           name="Tiles Y",
           description="A name for this item",
           default=0)

    framerate_prop = bpy.props.FloatProperty(
           name="Frame Rate",
           description="A name for this item",
           default=4.0)

    arm_tilesheetactionlist = bpy.props.CollectionProperty(type=ArmTilesheetActionListItem)
    arm_tilesheetactionlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

class ArmTilesheetList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmTilesheetListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_tilesheetlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        wrd.arm_tilesheetlist.add()
        wrd.arm_tilesheetlist_index = len(wrd.arm_tilesheetlist) - 1
        return{'FINISHED'}

class ArmTilesheetListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_tilesheetlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        wrd = bpy.data.worlds['Arm']
        return len(wrd.arm_tilesheetlist) > 0

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        list = wrd.arm_tilesheetlist
        index = wrd.arm_tilesheetlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        wrd.arm_tilesheetlist_index = index
        return{'FINISHED'}

class ArmTilesheetListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_tilesheetlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        wrd = bpy.data.worlds['Arm']
        return len(wrd.arm_tilesheetlist) > 0

    def move_index(self):
        # Move index of an item render queue while clamping it
        wrd = bpy.data.worlds['Arm']
        index = wrd.arm_tilesheetlist_index
        list_length = len(wrd.arm_tilesheetlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        list = wrd.arm_tilesheetlist
        index = wrd.arm_tilesheetlist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            #queue.move(index,neighbor)
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            #queue.move(neighbor, index)
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

def register():

    bpy.utils.register_class(ArmTilesheetActionListItem)
    bpy.utils.register_class(ArmTilesheetActionList)
    bpy.utils.register_class(ArmTilesheetActionListNewItem)
    bpy.utils.register_class(ArmTilesheetActionListDeleteItem)
    bpy.utils.register_class(ArmTilesheetActionListMoveItem)

    bpy.utils.register_class(ArmTilesheetListItem)
    bpy.utils.register_class(ArmTilesheetList)
    bpy.utils.register_class(ArmTilesheetListNewItem)
    bpy.utils.register_class(ArmTilesheetListDeleteItem)
    bpy.utils.register_class(ArmTilesheetListMoveItem)

    bpy.types.World.arm_tilesheetlist = bpy.props.CollectionProperty(type=ArmTilesheetListItem)
    bpy.types.World.arm_tilesheetlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

def unregister():
    bpy.utils.unregister_class(ArmTilesheetListItem)
    bpy.utils.unregister_class(ArmTilesheetList)
    bpy.utils.unregister_class(ArmTilesheetListNewItem)
    bpy.utils.unregister_class(ArmTilesheetListDeleteItem)
    bpy.utils.unregister_class(ArmTilesheetListMoveItem)

    bpy.utils.unregister_class(ArmTilesheetActionListItem)
    bpy.utils.unregister_class(ArmTilesheetActionList)
    bpy.utils.unregister_class(ArmTilesheetActionListNewItem)
    bpy.utils.unregister_class(ArmTilesheetActionListDeleteItem)
    bpy.utils.unregister_class(ArmTilesheetActionListMoveItem)
