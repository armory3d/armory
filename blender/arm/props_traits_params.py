import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmTraitParamListItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

class ArmTraitParamList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #layout.prop(item, "enabled_prop")
            #layout.label(text=item.name, icon = custom_icon)
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmTraitParamListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_traitparamslist.new_item"
    bl_label = "Add a new item"

    is_object = bpy.props.BoolProperty(name="", description="A name for this item", default=False)

    def execute(self, context):
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if len(obj.arm_traitlist) == 0:
            return
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        trait.arm_traitparamslist.add()
        trait.arm_traitparamslist_index = len(trait.arm_traitparamslist) - 1
        return{'FINISHED'}


class ArmTraitParamListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_traitparamslist.delete_item"
    bl_label = "Deletes an item"

    is_object = bpy.props.BoolProperty(name="", description="A name for this item", default=False)

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if obj == None:
            return False
        if len(obj.arm_traitlist) == 0:
            return False
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        return len(trait.arm_traitparamslist) > 0

    def execute(self, context):
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if len(obj.arm_traitlist) == 0:
            return
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        list = trait.arm_traitparamslist
        index = trait.arm_traitparamslist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        trait.arm_traitparamslist_index = index
        return{'FINISHED'}


class ArmTraitParamListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_traitparamslist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    is_object = bpy.props.BoolProperty(name="", description="A name for this item", default=False)

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if obj == None:
            return False
        if len(obj.arm_traitlist) == 0:
            return False
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        return len(trait.arm_traitparamslist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if len(obj.arm_traitlist) == 0:
            return
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        index = trait.arm_traitparamslist_index
        list_length = len(trait.arm_traitparamslist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        if self.is_object:
            obj = bpy.context.object
        else:
            obj = bpy.context.scene
        if len(obj.arm_traitlist) == 0:
            return
        trait = obj.arm_traitlist[obj.arm_traitlist_index]
        list = trait.arm_traitparamslist
        index = trait.arm_traitparamslist_index

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
    bpy.utils.register_class(ArmTraitParamListItem)
    bpy.utils.register_class(ArmTraitParamList)
    bpy.utils.register_class(ArmTraitParamListNewItem)
    bpy.utils.register_class(ArmTraitParamListDeleteItem)
    bpy.utils.register_class(ArmTraitParamListMoveItem)

def unregister():
    bpy.utils.unregister_class(ArmTraitParamListItem)
    bpy.utils.unregister_class(ArmTraitParamList)
    bpy.utils.unregister_class(ArmTraitParamListNewItem)
    bpy.utils.unregister_class(ArmTraitParamListDeleteItem)
    bpy.utils.unregister_class(ArmTraitParamListMoveItem)
