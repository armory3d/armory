import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def update_size_prop(self, context):
    if context.object == None:
        return
    mdata = context.object.data
    i = mdata.arm_lodlist_index
    ar = mdata.arm_lodlist
    # Clamp screen size to not exceed previous entry
    if i > 0 and ar[i - 1].screen_size_prop < self.screen_size_prop:
        self.screen_size_prop = ar[i - 1].screen_size_prop

class ArmLodListItem(bpy.types.PropertyGroup):
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

class ArmLodList(bpy.types.UIList):
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
            row.label(text=name, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text="{:.2f}".format(item.screen_size_prop))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmLodListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_lodlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.context.object.data
        mdata.arm_lodlist.add()
        mdata.arm_lodlist_index = len(mdata.arm_lodlist) - 1
        return{'FINISHED'}


class ArmLodListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_lodlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.context.object.data
        return len(mdata.arm_lodlist) > 0

    def execute(self, context):
        mdata = bpy.context.object.data
        lodlist = mdata.arm_lodlist
        index = mdata.arm_lodlist_index

        n = lodlist[index].name
        if n in context.scene.objects:
            obj = bpy.data.objects[n]
            context.scene.objects.unlink(obj)

        lodlist.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_lodlist_index = index
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmLodListItem)
    bpy.utils.register_class(ArmLodList)
    bpy.utils.register_class(ArmLodListNewItem)
    bpy.utils.register_class(ArmLodListDeleteItem)

    bpy.types.Mesh.arm_lodlist = bpy.props.CollectionProperty(type=ArmLodListItem)
    bpy.types.Mesh.arm_lodlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)
    bpy.types.Mesh.arm_lod_material = bpy.props.BoolProperty(name="Material Lod", description="Use materials of lod objects", default=False)

def unregister():
    bpy.utils.unregister_class(ArmLodListItem)
    bpy.utils.unregister_class(ArmLodList)
    bpy.utils.unregister_class(ArmLodListNewItem)
    bpy.utils.unregister_class(ArmLodListDeleteItem)
