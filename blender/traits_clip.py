import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ListClipTraitItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")
           
    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    start_prop = bpy.props.IntProperty(
           name="Start",
           description="A name for this item",
           default=0)

    end_prop = bpy.props.IntProperty(
           name="End",
           description="A name for this item",
           default=0)

    speed_prop = bpy.props.FloatProperty(
           name="Speed",
           description="A name for this item",
           default=1.0)

    loop_prop = bpy.props.BoolProperty(
           name="Loop",
           description="A name for this item",
           default=True)

    reflect_prop = bpy.props.BoolProperty(
           name="Reflect",
           description="A name for this item",
           default=False)


class MY_UL_ClipTraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            #layout.label(item.name, icon = custom_icon)
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class LIST_OT_ClipTraitNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_cliptraitlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        trait = context.object
        trait.my_cliptraitlist.add()
        trait.cliptraitlist_index = len(trait.my_cliptraitlist) - 1
        return{'FINISHED'}


class LIST_OT_ClipTraitDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_cliptraitlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        trait = context.object
        return len(trait.my_cliptraitlist) > 0

    def execute(self, context):
        trait = context.object
        list = trait.my_cliptraitlist
        index = trait.cliptraitlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        trait.cliptraitlist_index = index
        return{'FINISHED'}


class LIST_OT_ClipTraitMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_cliptraitlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        trait = context.object
        return len(trait.my_cliptraitlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        trait = context.object
        index = trait.cliptraitlist_index
        list_length = len(trait.my_cliptraitlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        trait = context.object
        list = trait.my_cliptraitlist
        index = trait.cliptraitlist_index

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
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
