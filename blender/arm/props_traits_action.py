import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ListActionTraitItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")
           
    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    action_name_prop = bpy.props.StringProperty(
           name="Action",
           description="A name for this item",
           default="")

class MY_UL_ActionTraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            layout.label(item.name, icon=custom_icon)
            # layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class LIST_OT_ActionTraitNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_actiontraitlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        trait = context.object.data
        trait.my_actiontraitlist.add()
        trait.actiontraitlist_index = len(trait.my_actiontraitlist) - 1
        return{'FINISHED'}


class LIST_OT_ActionTraitDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_actiontraitlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        trait = context.object.data
        return len(trait.my_actiontraitlist) > 0

    def execute(self, context):
        trait = context.object.data
        list = trait.my_actiontraitlist
        index = trait.actiontraitlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        trait.actiontraitlist_index = index
        return{'FINISHED'}


class LIST_OT_ActionTraitMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_actiontraitlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        trait = context.object.data
        return len(trait.my_actiontraitlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        trait = context.object.data
        index = trait.actiontraitlist_index
        list_length = len(trait.my_actiontraitlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        trait = context.object.data
        list = trait.my_actiontraitlist
        index = trait.actiontraitlist_index

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
    bpy.utils.register_class(ListActionTraitItem)
    bpy.utils.register_class(MY_UL_ActionTraitList)
    bpy.utils.register_class(LIST_OT_ActionTraitNewItem)
    bpy.utils.register_class(LIST_OT_ActionTraitDeleteItem)
    bpy.utils.register_class(LIST_OT_ActionTraitMoveItem)

def unregister():
    bpy.utils.unregister_class(ListActionTraitItem)
    bpy.utils.unregister_class(MY_UL_ActionTraitList)
    bpy.utils.unregister_class(LIST_OT_ActionTraitNewItem)
    bpy.utils.unregister_class(LIST_OT_ActionTraitDeleteItem)
    bpy.utils.unregister_class(LIST_OT_ActionTraitMoveItem)
