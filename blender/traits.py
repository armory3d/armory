import shutil
import bpy
import os
import json
from traits_animation import *
from traits_params import *
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import utils
import write_data
import subprocess

class ListTraitItem(bpy.types.PropertyGroup):
    # Group of properties representing an item in the list
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")
           
    enabled_prop = bpy.props.BoolProperty(
           name="",
           description="A name for this item",
           default=True)

    type_prop = bpy.props.EnumProperty(
        items = [('Script', 'Script', 'Script'),
                 ('Bundled Script', 'Bundled Script', 'Bundled Script'),
                 ('Nodes', 'Nodes', 'Nodes'),
                 ('Scene Instance', 'Scene Instance', 'Scene Instance'),
                 ('Animation', 'Animation', 'Animation')
                 ],
        name = "Type")

    data_prop = bpy.props.StringProperty(
           name="Data",
           description="A name for this item",
           default="")

    scene_prop = bpy.props.StringProperty(
           name="Scene",
           description="A name for this item",
           default="")

    class_name_prop = bpy.props.StringProperty(
           name="Class",
           description="A name for this item",
           default="")

    nodes_name_prop = bpy.props.StringProperty(
           name="Nodes",
           description="A name for this item",
           default="")

    start_track_name_prop = bpy.props.StringProperty(
           name="Start Track",
           description="A name for this item",
           default="")

    my_paramstraitlist = bpy.props.CollectionProperty(type=ListParamsTraitItem)
    paramstraitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

    my_animationtraitlist = bpy.props.CollectionProperty(type=ListAnimationTraitItem)
    animationtraitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

class MY_UL_TraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            layout.label(item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

def initObjectProperties():
    bpy.types.Object.my_traitlist = bpy.props.CollectionProperty(type = ListTraitItem)
    bpy.types.Object.traitlist_index = bpy.props.IntProperty(name = "Index for my_list", default=0)


class LIST_OT_TraitNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "my_traitlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        bpy.context.object.my_traitlist.add()
        bpy.context.object.traitlist_index = len(bpy.context.object.my_traitlist) - 1
        return{'FINISHED'}


class LIST_OT_TraitDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "my_traitlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        return len(bpy.context.object.my_traitlist) > 0

    def execute(self, context):
        list = bpy.context.object.my_traitlist
        index = bpy.context.object.traitlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        bpy.context.object.traitlist_index = index
        return{'FINISHED'}


class LIST_OT_TraitMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "my_traitlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list. """
        return len(bpy.context.object.my_traitlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        index = bpy.context.object.traitlist_index
        list_length = len(bpy.context.object.my_traitlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        list = bpy.context.object.my_traitlist
        index = bpy.context.object.traitlist_index

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

class ArmoryEditScriptButton(bpy.types.Operator):
    bl_idname = 'arm.edit_script'
    bl_label = 'Edit Script'
 
    def execute(self, context):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons['armory'].preferences
        sdk_path = addon_prefs.sdk_path
        kode_path = sdk_path + '/KodeStudio/KodeStudio.app/Contents/MacOS/Electron'
        project_path = utils.get_fp()
        item = context.object.my_traitlist[context.object.traitlist_index] 
        hx_path = project_path + '/Sources/' + bpy.data.worlds[0].ArmProjectPackage + '/' + item.class_name_prop + '.hx'
        subprocess.call([kode_path + ' ' + utils.get_fp() + ' ' + hx_path + ' &'], shell=True)
        return{'FINISHED'}

class ArmoryNewScriptDialog(bpy.types.Operator):
    bl_idname = "arm.new_script"
    bl_label = "New Script"
 
    class_name = StringProperty(name="Name")
 
    def execute(self, context):
        self.class_name = self.class_name.replace(' ', '')
        write_data.write_traithx(self.class_name)
        utils.fetch_script_names()
        obj = context.object
        item = obj.my_traitlist[obj.traitlist_index] 
        item.class_name_prop = self.class_name 
        return {'FINISHED'}
 
    def invoke(self, context, event):
        self.class_name = 'MyTrait'
        return context.window_manager.invoke_props_dialog(self)

class ArmoryRefreshScriptsListButton(bpy.types.Operator):
    bl_idname = 'arm.refresh_scripts_list'
    bl_label = 'Refresh Scripts List'
 
    def execute(self, context):
        utils.fetch_script_names()
        return{'FINISHED'}

# Menu in tools region
class ToolsTraitsPanel(bpy.types.Panel):
    bl_label = "Armory Traits"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        
        obj = bpy.context.object

        rows = 2
        if len(obj.my_traitlist) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("MY_UL_TraitList", "The_List", obj, "my_traitlist", obj, "traitlist_index", rows=rows)
        
        col = row.column(align=True)
        col.operator("my_traitlist.new_item", icon='ZOOMIN', text="")
        col.operator("my_traitlist.delete_item", icon='ZOOMOUT', text="")#.all = False

        if len(obj.my_traitlist) > 1:
            col.separator()
            col.operator("my_traitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("my_traitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if obj.traitlist_index >= 0 and len(obj.my_traitlist) > 0:
            item = obj.my_traitlist[obj.traitlist_index]         
            # Default props
            row = layout.row()
            row.prop(item, "type_prop")

            # Script
            if item.type_prop == 'Script' or item.type_prop == 'Bundled Script':
                item.name = item.class_name_prop
                row = layout.row()
                # row.prop(item, "class_name_prop")
                if item.type_prop == 'Script':
                    row.prop_search(item, "class_name_prop", bpy.data.worlds[0], "scripts_list", "Class")
                else:
                    row.prop_search(item, "class_name_prop", bpy.data.worlds[0], "bundled_scripts_list", "Class")
                # Params
                layout.label("Parameters")
                paramsrow = layout.row()
                paramsrows = 2
                if len(item.my_paramstraitlist) > 1:
                    paramsrows = 4
                
                row = layout.row()
                row.template_list("MY_UL_ParamsTraitList", "The_List", item, "my_paramstraitlist", item, "paramstraitlist_index", rows=paramsrows)

                col = row.column(align=True)
                col.operator("my_paramstraitlist.new_item", icon='ZOOMIN', text="")
                col.operator("my_paramstraitlist.delete_item", icon='ZOOMOUT', text="")

                if len(item.my_paramstraitlist) > 1:
                    col.separator()
                    col.operator("my_paramstraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("my_paramstraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if item.paramstraitlist_index >= 0 and len(item.my_paramstraitlist) > 0:
                    paramitem = item.my_paramstraitlist[item.paramstraitlist_index]   
                    # Picker
                    layout.label('Pickers')
                    layout.prop_search(paramitem, 'object_picker', bpy.context.scene, "objects", "Object")
                    layout.prop(paramitem, 'color_picker')

                if item.type_prop == 'Script':
                    row = layout.row()
                    if item.class_name_prop == '':
                        row.enabled = False
                    row.operator("arm.edit_script")
                    layout.operator("arm.new_script")
                    layout.operator("arm.refresh_scripts_list")
            
            # Nodes
            elif item.type_prop =='Nodes':
                item.name = item.nodes_name_prop
                row = layout.row()
                row.prop_search(item, "nodes_name_prop", bpy.data, "node_groups", "Tree")

            # Scene instance
            elif item.type_prop == 'Scene Instance':
                item.name = item.type_prop
                row = layout.row()
                row.prop_search(item, "scene_prop", bpy.data, "scenes", "Scene")
                #row.prop(item, "scene_prop")

            # Animation
            elif item.type_prop == 'Animation':
                item.name = item.type_prop
                row = layout.row()
                row.prop_search(item, "start_track_name_prop", item, "my_animationtraitlist", "Start Track")
                # Tracks list
                layout.label("Tracks")
                animrow = layout.row()
                animrows = 2
                if len(item.my_animationtraitlist) > 1:
                    animrows = 4
                
                row = layout.row()
                row.template_list("MY_UL_AnimationTraitList", "The_List", item, "my_animationtraitlist", item, "animationtraitlist_index", rows=animrows)

                col = row.column(align=True)
                col.operator("my_animationtraitlist.new_item", icon='ZOOMIN', text="")
                col.operator("my_animationtraitlist.delete_item", icon='ZOOMOUT', text="")

                if len(item.my_animationtraitlist) > 1:
                    col.separator()
                    col.operator("my_animationtraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("my_animationtraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if item.animationtraitlist_index >= 0 and len(item.my_animationtraitlist) > 0:
                    animitem = item.my_animationtraitlist[item.animationtraitlist_index]         
                    
                    row = layout.row()
                    row.prop(animitem, "start_prop")
                    row.prop(animitem, "end_prop")
                    layout.prop(animitem, "speed_prop")
                    layout.prop(animitem, "loop_prop")
                    layout.prop(animitem, "reflect_prop")

# Registration
def register():
    bpy.utils.register_module(__name__)
    initObjectProperties()

def unregister():
    bpy.utils.unregister_module(__name__)
