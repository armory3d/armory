import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmPropertyListItem(bpy.types.PropertyGroup):
    type_prop: EnumProperty(
        items = [('string', 'String', 'String'),
                 ('integer', 'Integer', 'Integer'),
                 ('float', 'Float', 'Float'),
                 ('boolean', 'Boolean', 'Boolean'),
                 ],
        name = "Type")
    name_prop: StringProperty(name="Name", description="A name for this item", default="my_prop")
    string_prop: StringProperty(name="String", description="A name for this item", default="text")
    integer_prop: IntProperty(name="Integer", description="A name for this item", default=0)
    float_prop: FloatProperty(name="Float", description="A name for this item", default=0.0)
    boolean_prop: BoolProperty(name="Boolean", description="A name for this item", default=False)

class ARM_UL_PropertyList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.use_property_split = False
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name_prop", text="", emboss=False, icon="OBJECT_DATAMODE")
            layout.prop(item, item.type_prop + "_prop", text="", emboss=(item.type_prop == 'boolean'))
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon="OBJECT_DATAMODE")

class ArmPropertyListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_propertylist.new_item"
    bl_label = "New"

    type_prop: EnumProperty(
        items = [('string', 'String', 'String'),
                 ('integer', 'Integer', 'Integer'),
                 ('float', 'Float', 'Float'),
                 ('boolean', 'Boolean', 'Boolean'),
                 ],
        name = "Type")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self,context):
        layout = self.layout
        layout.prop(self, "type_prop", expand=True)

    def execute(self, context):
        obj = bpy.context.object
        prop = obj.arm_propertylist.add()
        prop.type_prop = self.type_prop
        obj.arm_propertylist_index = len(obj.arm_propertylist) - 1
        return{'FINISHED'}

class ArmPropertyListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_propertylist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        obj = bpy.context.object
        if obj == None:
            return False
        return len(obj.arm_propertylist) > 0

    def execute(self, context):
        obj = bpy.context.object
        lst = obj.arm_propertylist
        index = obj.arm_propertylist_index

        if len(lst) <= index:
            return{'FINISHED'}

        lst.remove(index)

        if index > 0:
            index = index - 1

        obj.arm_propertylist_index = index
        return{'FINISHED'}

class ArmPropertyListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_propertylist.move_item"
    bl_label = "Move an item in the list"
    direction: EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        obj = bpy.context.object
        index = obj.arm_propertylist_index
        list_length = len(obj.arm_propertylist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        obj.arm_propertylist.move(index, new_index)
        obj.arm_propertylist_index = new_index

    def execute(self, context):
        obj = bpy.context.object
        list = obj.arm_propertylist
        index = obj.arm_propertylist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

def draw_properties(layout, obj):
    layout.label(text="Properties")
    rows = 2
    if len(obj.arm_traitlist) > 1:
        rows = 4
    row = layout.row()
    row.template_list("ARM_UL_PropertyList", "The_List", obj, "arm_propertylist", obj, "arm_propertylist_index", rows=rows)
    col = row.column(align=True)
    op = col.operator("arm_propertylist.new_item", icon='ADD', text="")
    op = col.operator("arm_propertylist.delete_item", icon='REMOVE', text="")
    if len(obj.arm_propertylist) > 1:
        col.separator()
        op = col.operator("arm_propertylist.move_item", icon='TRIA_UP', text="")
        op.direction = 'UP'
        op = col.operator("arm_propertylist.move_item", icon='TRIA_DOWN', text="")
        op.direction = 'DOWN'

def register():
    bpy.utils.register_class(ArmPropertyListItem)
    bpy.utils.register_class(ARM_UL_PropertyList)
    bpy.utils.register_class(ArmPropertyListNewItem)
    bpy.utils.register_class(ArmPropertyListDeleteItem)
    bpy.utils.register_class(ArmPropertyListMoveItem)
    bpy.types.Object.arm_propertylist = CollectionProperty(type=ArmPropertyListItem)
    bpy.types.Object.arm_propertylist_index = IntProperty(name="Index for arm_propertylist", default=0)

def unregister():
    bpy.utils.unregister_class(ArmPropertyListItem)
    bpy.utils.unregister_class(ARM_UL_PropertyList)
    bpy.utils.unregister_class(ArmPropertyListNewItem)
    bpy.utils.unregister_class(ArmPropertyListDeleteItem)
    bpy.utils.unregister_class(ArmPropertyListMoveItem)
