import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from arm.utils import to_hex

class ArmTraitPropListItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    value: StringProperty(
           name="Value",
           description="A name for this item",
           default="")

class ARM_UL_PropList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "value", text=item.name, emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

def register():
    bpy.utils.register_class(ArmTraitPropListItem)
    bpy.utils.register_class(ARM_UL_PropList)

def unregister():
    bpy.utils.unregister_class(ArmTraitPropListItem)
    bpy.utils.unregister_class(ARM_UL_PropList)
