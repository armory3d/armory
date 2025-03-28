import bpy
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
    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="")

    enabled_prop: BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    screen_size_prop: FloatProperty(
           name="Screen Size",
           description="A name for this item",
           min=0.0,
           max=1.0,
           default=0.0,
           update=update_size_prop)

class ARM_UL_LodList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.use_property_split = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.separator(factor=0.1)
            row.prop(item, "enabled_prop")
            name = item.name
            if name == '':
                name = 'None'
            row.label(text=name, icon='OBJECT_DATAMODE')
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text="{:.2f}".format(item.screen_size_prop))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='OBJECT_DATAMODE')

class ArmLodListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_lodlist.new_item"
    bl_label = "Add a new item"
    bl_options = {'UNDO'}

    def execute(self, context):
        mdata = bpy.context.object.data
        mdata.arm_lodlist.add()
        mdata.arm_lodlist_index = len(mdata.arm_lodlist) - 1
        return{'FINISHED'}


class ArmLodListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_lodlist.delete_item"
    bl_label = "Deletes an item"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """ Enable if there's something in the list """
        if bpy.context.object is None:
            return False
        mdata = bpy.context.object.data
        return len(mdata.arm_lodlist) > 0

    def execute(self, context):
        mdata = bpy.context.object.data
        lodlist = mdata.arm_lodlist
        index = mdata.arm_lodlist_index

        n = lodlist[index].name
        if n in context.scene.collection.objects:
            obj = bpy.data.objects[n]
            context.scene.collection.objects.unlink(obj)

        lodlist.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_lodlist_index = index
        return{'FINISHED'}

class ArmLodListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_lodlist.move_item"
    bl_label = "Move an item in the list"
    bl_options = {'INTERNAL', 'UNDO'}
    direction: EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        # Move index of an item render queue while clamping it
        mdata = bpy.context.object.data
        index = mdata.arm_lodlist_index
        list_length = len(mdata.arm_lodlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        mdata.arm_lodlist.move(index, new_index)
        mdata.arm_lodlist_index = new_index

    def execute(self, context):
        mdata = bpy.context.object.data
        list = mdata.arm_lodlist
        index = mdata.arm_lodlist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}


__REG_CLASSES = (
    ArmLodListItem,
    ARM_UL_LodList,
    ArmLodListNewItem,
    ArmLodListDeleteItem,
    ArmLodListMoveItem,
)
__reg_classes, unregister = bpy.utils.register_classes_factory(__REG_CLASSES)


def register():
    __reg_classes()

    bpy.types.Mesh.arm_lodlist = CollectionProperty(type=ArmLodListItem)
    bpy.types.Mesh.arm_lodlist_index = IntProperty(name="Index for my_list", default=0)
    bpy.types.Mesh.arm_lod_material = BoolProperty(name="Material Lod", description="Use materials of lod objects", default=False)
