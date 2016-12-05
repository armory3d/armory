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

def initObjectProperties():
    # Mesh only for now
    bpy.types.Mesh.my_lodlist = bpy.props.CollectionProperty(type=ListLodItem)
    bpy.types.Mesh.lodlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)
    bpy.types.Mesh.lod_material = bpy.props.BoolProperty(name="Material Lod", description="Use materials of lod objects", default=False)

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

class ArmoryGenerateLodButton(bpy.types.Operator):
    '''Automatically generate LoD levels'''
    bl_idname = 'arm.generate_lod'
    bl_label = 'Auto Generate'
 
    def lod_name(self, name, level):
        return name + '_LOD' + str(level + 1)

    def execute(self, context):
        obj = context.object
        if obj == None:
            return

        # Clear
        mdata = context.object.data
        mdata.lodlist_index = 0
        mdata.my_lodlist.clear()

        # Lod levels
        wrd = bpy.data.worlds['Arm']
        ratio = wrd.arm_lod_gen_ratio
        num_levels = wrd.arm_lod_gen_levels
        for level in range(0, num_levels):
            new_obj = obj.copy()
            for i in range(0, 3):
                new_obj.location[i] = 0
                new_obj.rotation_euler[i] = 0
                new_obj.scale[i] = 1
            new_obj.data = obj.data.copy()
            new_obj.name = self.lod_name(obj.name, level)
            new_obj.parent = obj
            new_obj.hide = True
            new_obj.hide_render = True
            mod = new_obj.modifiers.new('Decimate', 'DECIMATE')
            mod.ratio = ratio
            ratio *= wrd.arm_lod_gen_ratio
            context.scene.objects.link(new_obj)
            
        # Screen sizes
        for level in range(0, num_levels):
            mdata.my_lodlist.add()
            mdata.my_lodlist[-1].name = self.lod_name(obj.name, level)
            mdata.my_lodlist[-1].screen_size_prop = (1 - (1 / (num_levels + 1)) * level) - (1 / (num_levels + 1))

        return{'FINISHED'}

class ToolsLodPanel(bpy.types.Panel):
    bl_label = "Armory Lod"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        # Mesh only for now
        if obj.type != 'MESH':
            return

        mdata = obj.data
        layout.prop(mdata, "lod_material")

        rows = 2
        if len(mdata.my_lodlist) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("MY_UL_LodList", "The_List", mdata, "my_lodlist", mdata, "lodlist_index", rows=rows)
        col = row.column(align=True)
        col.operator("my_lodlist.new_item", icon='ZOOMIN', text="")
        col.operator("my_lodlist.delete_item", icon='ZOOMOUT', text="")

        if mdata.lodlist_index >= 0 and len(mdata.my_lodlist) > 0:
            item = mdata.my_lodlist[mdata.lodlist_index]
            row = layout.row()
            row.prop_search(item, "name", bpy.data, "objects", "Object")
            row = layout.row()
            row.prop(item, "screen_size_prop")

        # Auto lod for meshes
        if obj.type == 'MESH':
            layout.separator()
            layout.operator("arm.generate_lod")
            wrd = bpy.data.worlds['Arm']
            layout.prop(wrd, 'arm_lod_advanced')
            if wrd.arm_lod_advanced:
                layout.prop(wrd, 'arm_lod_gen_levels')
                layout.prop(wrd, 'arm_lod_gen_ratio')

def register():
    bpy.utils.register_module(__name__)
    initObjectProperties()

def unregister():
    bpy.utils.unregister_module(__name__)
