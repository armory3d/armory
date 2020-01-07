import bpy
from bpy.props import *

PROP_TYPE_ICONS = {
    "String": "SORTALPHA",
    "Int": "CHECKBOX_DEHLT",
    "Float": "RADIOBUT_OFF",
    "Bool": "CHECKMARK",
}


class ArmTraitPropListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    name: StringProperty(
        name="Name",
        description="The name of this property",
        default="Untitled")

    type: EnumProperty(
        items=(
            # (Haxe Type, Display Name, Description)
            ("String", "String", "String Type"),
            ("Int", "Integer", "Integer Type"),
            ("Float", "Float", "Float Type"),
            ("Bool", "Boolean", "Boolean Type")),
        name="Type",
        description="The type of this property",
        default="String")

    value_string: StringProperty(
        name="Value",
        description="The value of this property",
        default="")

    value_int: IntProperty(
        name="Value",
        description="The value of this property",
        default=0)

    value_float: FloatProperty(
        name="Value",
        description="The value of this property",
        default=0.0)

    value_bool: BoolProperty(
        name="Value",
        description="The value of this property",
        default=False)

    def set_value(self, val):
        if self.type == "Int":
            self.value_int = int(val)
        elif self.type == "Float":
            self.value_float = float(val)
        elif self.type == "Bool":
            self.value_bool = bool(val)
        else:
            self.value_string = str(val)

    def get_value(self):
        if self.type == "Int":
            return self.value_int
        if self.type == "Float":
            return self.value_float
        if self.type == "Bool":
            return self.value_bool
        return self.value_string


class ARM_UL_PropList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        item_value_ref = "value_" + item.type.lower()

        sp = layout.split(factor=0.2)
        # Some properties don't support icons
        sp.label(text=item.type, icon=PROP_TYPE_ICONS[item.type])
        sp = sp.split(factor=0.6)
        sp.label(text=item.name)

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            use_emboss = item.type == "Bool"
            sp.prop(item, item_value_ref, text="", emboss=use_emboss)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'


def register():
    bpy.utils.register_class(ArmTraitPropListItem)
    bpy.utils.register_class(ARM_UL_PropList)


def unregister():
    bpy.utils.unregister_class(ArmTraitPropListItem)
    bpy.utils.unregister_class(ARM_UL_PropList)
