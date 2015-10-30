import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *



class ListItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    type_prop = bpy.props.EnumProperty(
        items = [('Image', 'Image', 'Image'), 
                 ('Blob', 'Blob', 'Blob'), 
                 ('Sound', 'Sound', 'Sound'), 
                 ('Music', 'Music', 'Music'),
                 ('Font', 'Font', 'Font')],
        name = "Type")

    size_prop = bpy.props.IntProperty(
           name="Size",
           description="A name for this item",
           default=0)


bpy.utils.register_class(ListItem)



class MY_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            #layout.label(item.name, icon = custom_icon)
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)
bpy.utils.register_class(MY_UL_List)

    
    
def initWorldProperties():
    bpy.types.World.my_list = bpy.props.CollectionProperty(type = ListItem)
    bpy.types.World.list_index = bpy.props.IntProperty(name = "Index for my_list", default = 0)
initWorldProperties()



class LIST_OT_NewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        bpy.data.worlds[0].my_list.add()
        return{'FINISHED'}


class LIST_OT_DeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        return len(bpy.data.worlds[0].my_list) > 0

    def execute(self, context):
        list = bpy.data.worlds[0].my_list
        index = bpy.data.worlds[0].list_index

        list.remove(index)

        if index > 0:
            index = index - 1

        bpy.data.worlds[0].list_index = index
        return{'FINISHED'}


class LIST_OT_MoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_list.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        return len(bpy.data.worlds[0].my_list) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        index = bpy.data.worlds[0].list_index
        list_length = len(bpy.data.worlds[0].my_list) - 1 # (index starts at 0)
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        list = bpy.data.worlds[0].my_list
        index = bpy.data.worlds[0].list_index

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






#
# Menu in tools region
#
class ToolsAssetsPanel(bpy.types.Panel):
    bl_label = "zblend_assets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        scene = bpy.data.worlds[0]

        rows = 2
        if len(scene.my_list) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("MY_UL_List", "The_List", scene, "my_list", scene, "list_index", rows=rows)
        
        col = row.column(align=True)
        col.operator("my_list.new_item", icon='ZOOMIN', text="")
        col.operator("my_list.delete_item", icon='ZOOMOUT', text="")#.all = False

        if len(scene.my_list) > 1:
            col.separator()
            col.operator("my_list.move_item", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("my_list.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if scene.list_index >= 0 and len(scene.my_list) > 0:
            item = scene.my_list[scene.list_index]         
            #row = layout.row()
            #row.prop(item, "name")
            row = layout.row()
            row.prop(item, "type_prop")

            if item.type_prop == 'Font':
                row = layout.row()
                row.prop(item, "size_prop")


#
# Registration
#
bpy.utils.register_module(__name__)
