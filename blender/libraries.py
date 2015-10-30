import shutil
import bpy
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class LibListItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled")

    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)
bpy.utils.register_class(LibListItem)



class MY_UL_LibList(bpy.types.UIList):
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
bpy.utils.register_class(MY_UL_LibList)

    
    
def initWorldProperties():
    bpy.types.World.my_liblist = bpy.props.CollectionProperty(type = LibListItem)
    bpy.types.World.liblist_index = bpy.props.IntProperty(name = "Index for my_liblist", default = 0)
initWorldProperties()



class LIBLIST_OT_NewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_liblist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        bpy.data.worlds[0].my_liblist.add()
        return{'FINISHED'}


class LIBLIST_OT_DeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_liblist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        return len(bpy.data.worlds[0].my_liblist) > 0

    def execute(self, context):
        list = bpy.data.worlds[0].my_liblist
        index = bpy.data.worlds[0].liblist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        bpy.data.worlds[0].liblist_index = index
        return{'FINISHED'}


class LIST_OT_MoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_liblist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        return len(bpy.data.worlds[0].my_liblist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        index = bpy.data.worlds[0].liblist_index
        list_length = len(bpy.data.worlds[0].my_liblist) - 1 # (index starts at 0)
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        list = bpy.data.worlds[0].my_liblist
        index = bpy.data.worlds[0].liblist_index

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
class ToolsLibrariesPanel(bpy.types.Panel):
    bl_label = "zblend_libraries"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        scene = bpy.data.worlds[0]

        rows = 2
        if len(scene.my_liblist) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("MY_UL_LibList", "The_List", scene, "my_liblist", scene, "liblist_index", rows=rows)
        
        col = row.column(align=True)
        col.operator("my_liblist.new_item", icon='ZOOMIN', text="")
        col.operator("my_liblist.delete_item", icon='ZOOMOUT', text="")#.all = False

        if len(scene.my_liblist) > 1:
            col.separator()
            col.operator("my_liblist.move_item", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("my_liblist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        #if scene.liblist_index >= 0 and len(scene.my_liblist) > 0:
            #item = scene.my_liblist[scene.liblist_index]         
            #row = layout.row()
            #row.prop(item, "name")
            #row = layout.row()
            #row.prop(item, "type_prop")


#
# Registration
#
bpy.utils.register_module(__name__)
