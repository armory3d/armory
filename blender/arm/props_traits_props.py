import bpy
from bpy.props import *

PROP_TYPE_ICONS = {
    "String": "SORTALPHA",
    "Int": "CHECKBOX_DEHLT",
    "Float": "RADIOBUT_OFF",
    "Bool": "CHECKMARK",
    "Vec2": "ORIENTATION_VIEW",
    "Vec3": "ORIENTATION_GLOBAL",
    "Vec4": "MESH_ICOSPHERE",
    "Object": "OBJECT_DATA"
}


class ArmTraitPropWarning(bpy.types.PropertyGroup):
    warning: StringProperty(name="Warning")


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
            ("Bool", "Boolean", "Boolean Type"),
            ("Vec2", "Vec2", "2D Vector Type"),
            ("Vec3", "Vec3", "3D Vector Type"),
            ("Vec4", "Vec4", "4D Vector Type"),
            ("Object", "Object", "Object Type")),
        name="Type",
        description="The type of this property",
        default="String")

    # === VALUES ===
    value_string: StringProperty(name="Value", default="")
    value_int: IntProperty(name="Value", default=0)
    value_float: FloatProperty(name="Value", default=0.0)
    value_bool: BoolProperty(name="Value", default=False)
    value_vec2: FloatVectorProperty(name="Value", size=2)
    value_vec3: FloatVectorProperty(name="Value", size=3)
    value_vec4: FloatVectorProperty(name="Value", size=4)

    def set_value(self, val):
        # Would require way too much effort, so it's out of scope here.
        if self.type == "Object":
            return

        if self.type == "Int":
            self.value_int = int(val)
        elif self.type == "Float":
            self.value_float = float(val)
        elif self.type == "Bool":
            self.value_bool = bool(val)
        elif self.type in ("Vec2", "Vec3", "Vec4"):
            if isinstance(val, str):
                dimensions = int(self.type[-1])

                # Parse "new VecX(...)"
                val = val.split("(")[1].split(")")[0].split(",")
                val = [value.strip() for value in val]

                # new VecX() without parameters
                if len(val) == 1 and val[0] == "":
                    # Use default value
                    return

                # new VecX() with less parameters than its dimensions
                while len(val) < dimensions:
                    val.append(0.0)

                val = [float(value) for value in val]

            setattr(self, "value_" + self.type.lower(), val)
        else:
            self.value_string = str(val)

    def get_value(self):
        if self.type == "Int":
            return self.value_int
        if self.type == "Float":
            return self.value_float
        if self.type == "Bool":
            return self.value_bool
        if self.type in ("Vec2", "Vec3", "Vec4"):
            return list(getattr(self, "value_" + self.type.lower()))

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
            if item.type == "Object":
                sp.prop_search(item, "value_string", context.scene, "objects", text="")
            else:
                use_emboss = item.type == "Bool"
                sp.prop(item, item_value_ref, text="", emboss=use_emboss)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'


def register():
    bpy.utils.register_class(ArmTraitPropWarning)
    bpy.utils.register_class(ArmTraitPropListItem)
    bpy.utils.register_class(ARM_UL_PropList)


def unregister():
    bpy.utils.unregister_class(ARM_UL_PropList)
    bpy.utils.unregister_class(ArmTraitPropListItem)
    bpy.utils.unregister_class(ArmTraitPropWarning)
