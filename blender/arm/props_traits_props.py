import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from arm.utils import to_hex

class ListPropsTraitItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    value = bpy.props.StringProperty(
           name="Value",
           description="A name for this item",
           default="")

class MY_UL_PropsTraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.prop(item, "enabled_prop")
            #layout.label(item.name, icon = custom_icon)
            # layout.label(item.name)
            layout.prop(item, "value", text=item.name, emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

def register():
    bpy.utils.register_class(ListPropsTraitItem)
    bpy.utils.register_class(MY_UL_PropsTraitList)

def unregister():
    bpy.utils.unregister_class(ListPropsTraitItem)
    bpy.utils.unregister_class(MY_UL_PropsTraitList)
