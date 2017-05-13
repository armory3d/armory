import shutil
import bpy
import subprocess
import os
import json
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from arm.props_traits_params import *
import arm.utils
import arm.write_data as write_data

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
        items = [('Haxe Script', 'Haxe Script', 'Haxe Script'),
                 ('Python Script', 'Python Script', 'Python Script'),
                 ('JS Script', 'JS Script', 'JS Script'),
                 ('Bundled Script', 'Bundled Script', 'Bundled Script'),
                 ('Logic Nodes', 'Logic Nodes', 'Logic Nodes')
                 ],
        name = "Type")

    # data_prop = bpy.props.StringProperty(
    #        name="Data",
    #        description="A name for this item",
    #        default="")

    class_name_prop = bpy.props.StringProperty(
           name="Class",
           description="A name for this item",
           default="")

    jsscript_prop = bpy.props.StringProperty(
           name="Text",
           description="A name for this item",
           default="")

    nodes_name_prop = bpy.props.StringProperty(
           name="Nodes",
           description="A name for this item",
           default="")

    my_paramstraitlist = bpy.props.CollectionProperty(type=ListParamsTraitItem)
    paramstraitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

class MY_UL_TraitList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "enabled_prop")
            layout.label(item.name, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

def initObjectProperties():
    bpy.types.Object.my_traitlist = bpy.props.CollectionProperty(type=ListTraitItem)
    bpy.types.Object.traitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)


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
    '''Edit script in Kode Studio'''
    bl_idname = 'arm.edit_script'
    bl_label = 'Edit Script'
 
    def execute(self, context):
        project_path = arm.utils.get_fp()
        item = context.object.my_traitlist[context.object.traitlist_index]
        pkg = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package)
        hx_path = project_path + '/Sources/' + pkg + '/' + item.class_name_prop + '.hx'

        sdk_path = arm.utils.get_sdk_path()
        if arm.utils.get_os() == 'win':
            kode_path = sdk_path + '/win32/Kode Studio.exe'
            subprocess.Popen([kode_path, arm.utils.get_fp(), hx_path])
        elif arm.utils.get_os() == 'mac':
            kode_path = '"' + sdk_path + '/Kode Studio.app/Contents/MacOS/Electron"'
            subprocess.Popen([kode_path + ' "' + arm.utils.get_fp() + '" "' + hx_path + '"'], shell=True)
        else:
            kode_path = sdk_path + '/linux64/kodestudio'
            subprocess.Popen([kode_path, arm.utils.get_fp(), hx_path])
        
        return{'FINISHED'}

class ArmoryEditBundledScriptButton(bpy.types.Operator):
    '''Copy script to project and edit in Kode Studio'''
    bl_idname = 'arm.edit_bundled_script'
    bl_label = 'Edit Script'
 
    def execute(self, context):
        sdk_path = arm.utils.get_sdk_path()
        project_path = arm.utils.get_fp()
        pkg = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package)
        item = context.object.my_traitlist[context.object.traitlist_index]  
        source_hx_path = sdk_path + '/armory/Sources/armory/trait/' + item.class_name_prop + '.hx'
        target_hx_path = project_path + '/Sources/' + pkg + '/' + item.class_name_prop + '.hx'

        if not os.path.isfile(target_hx_path):
            # Rewrite package and copy
            sf = open(source_hx_path)
            sf.readline()
            tf = open(target_hx_path, 'w')
            tf.write('package ' + pkg + ';\n')
            shutil.copyfileobj(sf, tf)
            sf.close()
            tf.close()
            arm.utils.fetch_script_names()

        # From bundled to script
        item.type_prop = 'Haxe Script'

        # Edit in Kode Studio
        bpy.ops.arm.edit_script('EXEC_DEFAULT')
        
        return{'FINISHED'}

class ArmoryNewScriptDialog(bpy.types.Operator):
    '''Create blank script'''
    bl_idname = "arm.new_script"
    bl_label = "New Script"
 
    class_name = StringProperty(name="Name")
 
    def execute(self, context):
        self.class_name = self.class_name.replace(' ', '')
        write_data.write_traithx(self.class_name)
        arm.utils.fetch_script_names()
        obj = context.object
        item = obj.my_traitlist[obj.traitlist_index] 
        item.class_name_prop = self.class_name 
        return {'FINISHED'}
 
    def invoke(self, context, event):
        if not arm.utils.check_saved(self):
            return {'CANCELLED'}
        self.class_name = 'MyTrait'
        return context.window_manager.invoke_props_dialog(self)

class ArmoryRefreshScriptsListButton(bpy.types.Operator):
    '''Fetch all script names'''
    bl_idname = 'arm.refresh_scripts_list'
    bl_label = 'Refresh Scripts List'
 
    def execute(self, context):
        arm.utils.fetch_bundled_script_names()
        arm.utils.fetch_script_names()
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
            if item.type_prop == 'Haxe Script' or item.type_prop == 'Bundled Script':
                item.name = item.class_name_prop
                row = layout.row()
                # row.prop(item, "class_name_prop")
                if item.type_prop == 'Haxe Script':
                    row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "scripts_list", "Class")
                else:
                    row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "bundled_scripts_list", "Class")
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

                if item.type_prop == 'Haxe Script':
                    row = layout.row()
                    if item.class_name_prop == '':
                        row.enabled = False
                    row.operator("arm.edit_script")
                    layout.operator("arm.new_script")
                    layout.operator("arm.refresh_scripts_list")
                else: # Bundled
                    layout.operator("arm.edit_bundled_script")
            
            # JS/Python Script
            elif item.type_prop == 'JS Script' or item.type_prop == 'Python Script':
                item.name = item.jsscript_prop
                row = layout.row()
                row.prop_search(item, "jsscript_prop", bpy.data, "texts", "Text")

            # Nodes
            elif item.type_prop == 'Logic Nodes':
                item.name = item.nodes_name_prop
                row = layout.row()
                row.prop_search(item, "nodes_name_prop", bpy.data, "node_groups", "Tree")

def register():  
    bpy.utils.register_class(ListTraitItem)
    bpy.utils.register_class(MY_UL_TraitList)
    bpy.utils.register_class(LIST_OT_TraitNewItem)
    bpy.utils.register_class(LIST_OT_TraitDeleteItem)
    bpy.utils.register_class(LIST_OT_TraitMoveItem)
    bpy.utils.register_class(ArmoryEditScriptButton)
    bpy.utils.register_class(ArmoryEditBundledScriptButton)
    bpy.utils.register_class(ArmoryNewScriptDialog)
    bpy.utils.register_class(ArmoryRefreshScriptsListButton)
    bpy.utils.register_class(ToolsTraitsPanel)

    initObjectProperties()

def unregister():
    bpy.utils.unregister_class(ListTraitItem)
    bpy.utils.unregister_class(MY_UL_TraitList)
    bpy.utils.unregister_class(LIST_OT_TraitNewItem)
    bpy.utils.unregister_class(LIST_OT_TraitDeleteItem)
    bpy.utils.unregister_class(LIST_OT_TraitMoveItem)
    bpy.utils.unregister_class(ArmoryEditScriptButton)
    bpy.utils.unregister_class(ArmoryEditBundledScriptButton)
    bpy.utils.unregister_class(ArmoryNewScriptDialog)
    bpy.utils.unregister_class(ArmoryRefreshScriptsListButton)
    bpy.utils.unregister_class(ToolsTraitsPanel)
