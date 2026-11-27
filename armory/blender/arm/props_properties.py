import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import arm.utils



class ArmArrayItem(bpy.types.PropertyGroup):
    # Name property for each array item
    name_prop: StringProperty(name="Name", default="Item")
    index_prop = bpy.props.IntProperty(
        name="Index",
        description="Index of the item",
        default=0,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    # Properties for each type
    string_prop: StringProperty(name="String", default="")
    integer_prop: IntProperty(name="Integer", default=0)
    float_prop: FloatProperty(name="Float", default=0.0)
    boolean_prop: BoolProperty(name="Boolean", default=False)
  

class ArmPropertyListItem(bpy.types.PropertyGroup):
    type_prop: EnumProperty(
        items = [('string', 'String', 'String'),
                 ('integer', 'Integer', 'Integer'),
                 ('float', 'Float', 'Float'),
                 ('boolean', 'Boolean', 'Boolean'),
                 ('array', 'Array', 'Array'),                 
                 ],
        name = "Type")
    name_prop: StringProperty(name="Name", description="A name for this item", default="my_prop")
    string_prop: StringProperty(name="String", description="A name for this item", default="text")
    integer_prop: IntProperty(name="Integer", description="A name for this item", default=0)
    float_prop: FloatProperty(name="Float", description="A name for this item", default=0.0)
    boolean_prop: BoolProperty(name="Boolean", description="A name for this item", default=False)
    array_prop: CollectionProperty(type=ArmArrayItem)
    array_item_type: EnumProperty(
        items = [
            ('string', 'String', 'String'),
            ('integer', 'Integer', 'Integer'),
            ('float', 'Float', 'Float'),
            ('boolean', 'Boolean', 'Boolean'),
            # Add more types here as needed
        ],
        name = "New Item Type",
        default = 'string'
    )
    
class ARM_UL_ArrayItemList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Use the item's index within the array as its uneditable name
        array_type = data.array_item_type
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Display the index of the item as its name in a non-editable label
            layout.label(text=str(index))

            # Display the appropriate property based on the array type
            if array_type == 'string':
                layout.prop(item, "string_prop", text="")
            elif array_type == 'integer':
                layout.prop(item, "integer_prop", text="")
            elif array_type == 'float':
                layout.prop(item, "float_prop", text="")
            elif array_type == 'boolean':
                layout.prop(item, "boolean_prop", text="")
            # Add other types as needed
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon="OBJECT_DATAMODE")

            
class ArmArrayAddItem(bpy.types.Operator):
    bl_idname = "arm_array.add_item"
    bl_label = "Add Array Item"

    def execute(self, context):
        obj = bpy.context.object
        if obj.arm_propertylist and obj.arm_propertylist_index < len(obj.arm_propertylist):
            selected_item = obj.arm_propertylist[obj.arm_propertylist_index]

            # Create a new item in the array
            new_item = selected_item.array_prop.add()

            # Set the type of the new item based on the selected type
            new_item_type = selected_item.array_item_type
            if new_item_type == 'string':
                new_item.string_prop = ""  # Default value for string
            elif new_item_type == 'integer':
                new_item.integer_prop = 0  # Default value for integer
            elif new_item_type == 'float':
                new_item.float_prop = 0.0  # Default value for float
            elif new_item_type == 'boolean':
                new_item.boolean_prop = False  # Default value for boolean

            # Set the index of the new item
            new_item_index = len(selected_item.array_prop) - 1
            new_item.index_prop = new_item_index

            # Update the array index
            selected_item.array_index = new_item_index

        return {'FINISHED'}

# Operator to remove an item from the array
class ArmArrayRemoveItem(bpy.types.Operator):
    bl_idname = "arm_array.remove_item"
    bl_label = "Remove Array Item"

    def execute(self, context):
        obj = bpy.context.object
        if obj.arm_propertylist and obj.arm_propertylist_index < len(obj.arm_propertylist):
            selected_item = obj.arm_propertylist[obj.arm_propertylist_index]
            if selected_item.array_prop:
                selected_item.array_prop.remove(selected_item.array_index)
                if selected_item.array_index > 0:
                    selected_item.array_index -= 1
        return {'FINISHED'}

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
                 ('array', 'Array', 'Array'),                 
                 
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


class ARM_OT_CopyArmoryPropsToSelected(bpy.types.Operator):
    bl_label = 'Copy Armory Props to Selected Objects'
    bl_idname = 'arm.copy_armory_props_to_selected'
    bl_description = 'Copies Armory object properties of the active object to all other selected objects'

    overwrite: BoolProperty(name="Overwrite", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.selected_objects) > 1

    def draw_message_box(self, context):
        layout = self.layout
        layout = layout.column(align=True)
        layout.alignment = 'EXPAND'

        layout.label(text='Warning: At least one target object already has', icon='ERROR')
        layout.label(text='custom properties assigned to it!', icon='BLANK1')
        layout.separator()
        layout.label(text='Do you want to overwrite existing properties', icon='BLANK1')
        layout.label(text='or append to them?', icon='BLANK1')
        layout.separator()

        row = layout.row(align=True)
        row.active_default = True
        row.operator('arm.copy_armory_props_to_selected', text='Overwrite').overwrite = True
        row.active_default = False
        row.operator('arm.copy_armory_props_to_selected', text='Append').overwrite = False
        row.operator('arm.discard_popup', text='Cancel')

    def execute(self, context):
        source_obj = bpy.context.active_object

        # Armory object-level settings to copy
        object_settings = [
            'arm_sorting_index',
            'arm_export',
            'arm_spawn',
            'arm_mobile',
            'arm_animation_enabled',
            'arm_lighting',
            'arm_instanced',
        ]

        for target_obj in bpy.context.selected_objects:
            if source_obj == target_obj:
                continue

            # Copy object-level Armory flags
            for prop in object_settings:
                if hasattr(source_obj, prop) and hasattr(target_obj, prop):
                    setattr(target_obj, prop, getattr(source_obj, prop))

            # Offset for property iteration when appending properties
            offset = 0
            if not self.overwrite:
                offset = len(target_obj.arm_propertylist)

            arm.utils.merge_into_collection(
                source_obj.arm_propertylist, target_obj.arm_propertylist, clear_dst=self.overwrite)

            for i in range(len(source_obj.arm_propertylist)):
                if i + offset < len(target_obj.arm_propertylist):
                    arm.utils.merge_into_collection(
                        source_obj.arm_propertylist[i].array_prop,
                        target_obj.arm_propertylist[i + offset].array_prop,
                        clear_dst=True
                    )

        return {"FINISHED"}

    def invoke(self, context, event):
        show_dialog = False

        source_obj = bpy.context.active_object
        for target_object in bpy.context.selected_objects:
            if source_obj == target_object:
                continue
            else:
                if target_object.arm_propertylist:
                    show_dialog = True
                    break

        if show_dialog:
            context.window_manager.popover(self.__class__.draw_message_box, ui_units_x=16)
        else:
            bpy.ops.arm.copy_armory_props_to_selected(overwrite=self.overwrite)

        return {'INTERFACE'}


def draw_properties(layout, obj):
    layout.label(text="Properties")

    # Draw the ARM_UL_PropertyList
    rows = 4 if len(obj.arm_propertylist) > 1 else 2
    row = layout.row()
    row.template_list("ARM_UL_PropertyList", "The_List", obj, "arm_propertylist", obj, "arm_propertylist_index", rows=rows)

    # Column for buttons next to ARM_UL_PropertyList
    col = row.column(align=True)
    col.operator("arm_propertylist.new_item", icon='ADD', text="")
    col.operator("arm_propertylist.delete_item", icon='REMOVE', text="")
    col.operator("arm.copy_armory_props_to_selected", icon='PASTEDOWN', text="")
    if len(obj.arm_propertylist) > 1:
        col.separator()
        col.operator("arm_propertylist.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("arm_propertylist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

    # Draw UI List for array items if the selected property is an array
    if obj.arm_propertylist and obj.arm_propertylist_index < len(obj.arm_propertylist):
        selected_item = obj.arm_propertylist[obj.arm_propertylist_index]
        if selected_item.type_prop == 'array':
            layout.label(text="Array Items")

            # Dropdown to select the type of new array items
            layout.prop(selected_item, "array_item_type", text="Array Type")

            # Template list for array items
            row = layout.row()
            row.template_list("ARM_UL_ArrayItemList", "", selected_item, "array_prop", selected_item, "array_index", rows=rows)

            # Column for buttons next to the array items list
            col = row.column(align=True)
            col.operator("arm_array.add_item", icon='ADD', text="")
            col.operator("arm_array.remove_item", icon='REMOVE', text="")


__REG_CLASSES = (
    ArmArrayItem,
    ArmPropertyListItem,
    ARM_UL_PropertyList,
    ARM_UL_ArrayItemList,
    ArmPropertyListNewItem,
    ArmPropertyListDeleteItem,
    ArmPropertyListMoveItem,
    ArmArrayAddItem,
    ArmArrayRemoveItem,
    ARM_OT_CopyArmoryPropsToSelected,
)
__reg_classes, unregister = bpy.utils.register_classes_factory(__REG_CLASSES)


def register():
    __reg_classes()
    bpy.types.Object.arm_propertylist = CollectionProperty(type=ArmPropertyListItem)
    bpy.types.Object.arm_propertylist_index = IntProperty(name="Index for arm_propertylist", default=0)
    # New property for tracking the active index in array items
    bpy.types.PropertyGroup.array_index = IntProperty(name="Array Index", default=0)

