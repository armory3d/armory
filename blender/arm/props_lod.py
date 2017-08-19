import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def update_size_prop(self, context):
    if context.object == None:
        return
    mdata = context.object.data
    i = mdata.lodlist_index
    ar = mdata.my_lodlist
    # Clamp screen size to not exceed previous entry
    if i > 0 and ar[i - 1].screen_size_prop < self.screen_size_prop:
        self.screen_size_prop = ar[i - 1].screen_size_prop

class ListLodItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")
           
    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    screen_size_prop = bpy.props.FloatProperty(
           name="Screen Size",
           description="A name for this item",
           min=0.0,
           max=1.0,
           default=0.0,
           update=update_size_prop)

class MY_UL_LodList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            name = item.name
            if name == '':
                name = 'None'
            row = layout.row()
            row.label(name, icon=custom_icon)
            row.alignment = 'RIGHT'
            row.label("{:.2f}".format(item.screen_size_prop))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class LIST_OT_LodNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_lodlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.context.object.data
        mdata.my_lodlist.add()
        mdata.lodlist_index = len(mdata.my_lodlist) - 1
        return{'FINISHED'}


class LIST_OT_LodDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_lodlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.context.object.data
        return len(mdata.my_lodlist) > 0

    def execute(self, context):
        mdata = bpy.context.object.data
        list = mdata.my_lodlist
        index = mdata.lodlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        mdata.lodlist_index = index
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ListLodItem)
    bpy.utils.register_class(MY_UL_LodList)
    bpy.utils.register_class(LIST_OT_LodNewItem)
    bpy.utils.register_class(LIST_OT_LodDeleteItem)

def unregister():
    bpy.utils.unregister_class(ListLodItem)
    bpy.utils.unregister_class(MY_UL_LodList)
    bpy.utils.unregister_class(LIST_OT_LodNewItem)
    bpy.utils.unregister_class(LIST_OT_LodDeleteItem)
