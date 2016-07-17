import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from utils import to_hex

def object_picker_update(self, context):
    o = context.object
    tl = o.my_traitlist[o.traitlist_index]
    pl = tl.my_paramstraitlist[tl.paramstraitlist_index]
    pl.name = "'" + pl.object_picker + "'"

def color_picker_update(self, context):
    o = context.object
    tl = o.my_traitlist[o.traitlist_index]
    pl = tl.my_paramstraitlist[tl.paramstraitlist_index]
    col = pl.color_picker
    pl.name = str(to_hex(col))

class ListParamsTraitItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    object_picker = bpy.props.StringProperty(
           name="Object",
           description="A name for this item",
           default="",
           update=object_picker_update)

    color_picker = bpy.props.FloatVectorProperty(
           name="Color",
           description="A name for this item",
           size=4,
           subtype='COLOR',
           default=[1, 1, 1, 1],
           update=color_picker_update)

class MY_UL_ParamsTraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.prop(item, "enabled_prop")
            #layout.label(item.name, icon = custom_icon)
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class LIST_OT_ParamsTraitNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_paramstraitlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        trait = context.object.my_traitlist[context.object.traitlist_index]
        trait.my_paramstraitlist.add()
        trait.paramstraitlist_index = len(trait.my_paramstraitlist) - 1
        return{'FINISHED'}


class LIST_OT_ParamsTraitDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_paramstraitlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        trait = context.object.my_traitlist[context.object.traitlist_index]
        return len(trait.my_paramstraitlist) > 0

    def execute(self, context):
        trait = context.object.my_traitlist[context.object.traitlist_index]
        list = trait.my_paramstraitlist
        index = trait.paramstraitlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        trait.paramstraitlist_index = index
        return{'FINISHED'}


class LIST_OT_ParamsTraitMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_paramstraitlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        trait = context.object.my_traitlist[context.object.traitlist_index]
        return len(trait.my_paramstraitlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        trait = context.object.my_traitlist[context.object.traitlist_index]
        index = trait.paramstraitlist_index
        list_length = len(trait.my_paramstraitlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        trait = context.object.my_traitlist[context.object.traitlist_index]
        list = trait.my_paramstraitlist
        index = trait.paramstraitlist_index

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
