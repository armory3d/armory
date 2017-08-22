import shutil
import bpy
import subprocess
import os
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from arm.props_traits_params import *
from arm.props_traits_props import *
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
                 ('JS Script', 'JS Script', 'JS Script'),
                 ('UI Canvas', 'UI Canvas', 'UI Canvas'),
                 ('Bundled Script', 'Bundled Script', 'Bundled Script'),
                 ('Logic Nodes', 'Logic Nodes', 'Logic Nodes')
                 ],
        name = "Type")

    class_name_prop = bpy.props.StringProperty(
           name="Class",
           description="A name for this item",
           default="")

    canvas_name_prop = bpy.props.StringProperty(
           name="Canvas",
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

class ArmTraitListItem(bpy.types.PropertyGroup):
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
                 ('JS Script', 'JS Script', 'JS Script'),
                 ('UI Canvas', 'UI Canvas', 'UI Canvas'),
                 ('Bundled Script', 'Bundled Script', 'Bundled Script'),
                 ('Logic Nodes', 'Logic Nodes', 'Logic Nodes')
                 ],
        name = "Type")

    class_name_prop = bpy.props.StringProperty(
           name="Class",
           description="A name for this item",
           default="")

    canvas_name_prop = bpy.props.StringProperty(
           name="Canvas",
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

    arm_traitparamslist = bpy.props.CollectionProperty(type=ArmTraitParamListItem)
    arm_traitparamslist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

    arm_traitpropslist = bpy.props.CollectionProperty(type=ArmTraitPropListItem)
    arm_traitpropslist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

class ArmTraitList(bpy.types.UIList):
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

class ArmTraitListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_traitlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        trait = bpy.context.object.arm_traitlist.add()
        bpy.context.object.arm_traitlist_index = len(bpy.context.object.arm_traitlist) - 1
        return{'FINISHED'}


class ArmTraitListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_traitlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        if bpy.context.object == None:
            return False
        return len(bpy.context.object.arm_traitlist) > 0

    def execute(self, context):
        list = bpy.context.object.arm_traitlist
        index = bpy.context.object.arm_traitlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        bpy.context.object.arm_traitlist_index = index
        return{'FINISHED'}


class ArmTraitListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_traitlist.move_item"
    bl_label = "Move an item in the list"
    direction = bpy.props.EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    @classmethod
    def poll(self, context):
        if bpy.context.object == None:
            return False
        """ Enable if there's something in the list. """
        return len(bpy.context.object.arm_traitlist) > 0


    def move_index(self):
        # Move index of an item render queue while clamping it
        index = bpy.context.object.arm_traitlist_index
        list_length = len(bpy.context.object.arm_traitlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        index = new_index


    def execute(self, context):
        list = bpy.context.object.arm_traitlist
        index = bpy.context.object.arm_traitlist_index

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

class ArmEditScriptButton(bpy.types.Operator):
    '''Edit script in Kode Studio'''
    bl_idname = 'arm.edit_script'
    bl_label = 'Edit Script'
 
    def execute(self, context):
        project_path = arm.utils.get_fp()
        item = context.object.arm_traitlist[context.object.arm_traitlist_index]
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

class ArmEditBundledScriptButton(bpy.types.Operator):
    '''Copy script to project and edit in Kode Studio'''
    bl_idname = 'arm.edit_bundled_script'
    bl_label = 'Edit Script'
 
    def execute(self, context):
        sdk_path = arm.utils.get_sdk_path()
        project_path = arm.utils.get_fp()
        pkg = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package)
        item = context.object.arm_traitlist[context.object.arm_traitlist_index]  
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

class ArmEditCanvasButton(bpy.types.Operator):
    '''Edit ui canvas'''
    bl_idname = 'arm.edit_canvas'
    bl_label = 'Edit Canvas'
 
    def execute(self, context):
        project_path = arm.utils.get_fp()
        item = context.object.arm_traitlist[context.object.arm_traitlist_index]
        canvas_path = project_path + '/Bundled/canvas/' + item.canvas_name_prop + '.json'
        write_data.write_canvasprefs(canvas_path)

        sdk_path = arm.utils.get_sdk_path()
        armorui_path = sdk_path + '/armory/tools/armorui/krom'
        krom_location, krom_path = arm.utils.krom_paths()
        os.chdir(krom_location)
        subprocess.Popen([krom_path, armorui_path, armorui_path, '--nosound'])
        return{'FINISHED'}

class ArmNewScriptDialog(bpy.types.Operator):
    '''Create blank script'''
    bl_idname = "arm.new_script"
    bl_label = "New Script"
 
    class_name = StringProperty(name="Name")
 
    def execute(self, context):
        self.class_name = self.class_name.replace(' ', '')
        write_data.write_traithx(self.class_name)
        arm.utils.fetch_script_names()
        obj = context.object
        item = obj.arm_traitlist[obj.arm_traitlist_index] 
        item.class_name_prop = self.class_name 
        return {'FINISHED'}
 
    def invoke(self, context, event):
        if not arm.utils.check_saved(self):
            return {'CANCELLED'}
        self.class_name = 'MyTrait'
        return context.window_manager.invoke_props_dialog(self)

class ArmNewCanvasDialog(bpy.types.Operator):
    '''Create blank canvas'''
    bl_idname = "arm.new_canvas"
    bl_label = "New Canvas"
 
    canvas_name = StringProperty(name="Name")
 
    def execute(self, context):
        self.canvas_name = self.canvas_name.replace(' ', '')
        write_data.write_canvasjson(self.canvas_name)
        arm.utils.fetch_script_names()
        obj = context.object
        item = obj.arm_traitlist[obj.arm_traitlist_index] 
        item.canvas_name_prop = self.canvas_name 
        return {'FINISHED'}
 
    def invoke(self, context, event):
        if not arm.utils.check_saved(self):
            return {'CANCELLED'}
        self.canvas_name = 'MyCanvas'
        return context.window_manager.invoke_props_dialog(self)

class ArmRefreshScriptsButton(bpy.types.Operator):
    '''Fetch all script names'''
    bl_idname = 'arm.refresh_scripts'
    bl_label = 'Refresh'
 
    def execute(self, context):
        arm.utils.fetch_bundled_script_names()
        arm.utils.fetch_script_names()
        arm.utils.fetch_trait_props()
        return{'FINISHED'}

class ArmRefreshCanvasListButton(bpy.types.Operator):
    '''Fetch all canvas names'''
    bl_idname = 'arm.refresh_canvas_list'
    bl_label = 'Refresh'
 
    def execute(self, context):
        arm.utils.fetch_script_names()
        return{'FINISHED'}

# Menu in tools region
class ArmTraitsPanel(bpy.types.Panel):
    bl_label = "Armory Traits"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        
        obj = bpy.context.object

        rows = 2
        if len(obj.arm_traitlist) > 1:
            rows = 4
        
        row = layout.row()
        row.template_list("ArmTraitList", "The_List", obj, "arm_traitlist", obj, "arm_traitlist_index", rows=rows)
        
        col = row.column(align=True)
        col.operator("arm_traitlist.new_item", icon='ZOOMIN', text="")
        col.operator("arm_traitlist.delete_item", icon='ZOOMOUT', text="")#.all = False

        if len(obj.arm_traitlist) > 1:
            col.separator()
            col.operator("arm_traitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("arm_traitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if obj.arm_traitlist_index >= 0 and len(obj.arm_traitlist) > 0:
            item = obj.arm_traitlist[obj.arm_traitlist_index]
            # Default props
            row = layout.row()
            row.prop(item, "type_prop")

            # Script
            if item.type_prop == 'Haxe Script' or item.type_prop == 'Bundled Script':
                item.name = item.class_name_prop
                row = layout.row()
                # row.prop(item, "class_name_prop")
                if item.type_prop == 'Haxe Script':
                    row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "arm_scripts_list", "Class")
                else:
                    row.prop_search(item, "class_name_prop", bpy.data.worlds['Arm'], "arm_bundled_scripts_list", "Class")
                
                # Props
                if len(item.arm_traitpropslist) > 0:
                    propsrow = layout.row()
                    propsrows = 2
                    if len(item.arm_traitpropslist) > 2:
                        propsrows = 4
                    row = layout.row()
                    row.template_list("ArmTraitPropList", "The_List", item, "arm_traitpropslist", item, "arm_traitpropslist_index", rows=propsrows)
                
                # Params
                layout.label("Parameters")
                paramsrow = layout.row()
                paramsrows = 2
                if len(item.arm_traitparamslist) > 1:
                    paramsrows = 4
                
                row = layout.row()
                row.template_list("ArmTraitParamList", "The_List", item, "arm_traitparamslist", item, "arm_traitparamslist_index", rows=paramsrows)

                col = row.column(align=True)
                col.operator("arm_traitparamslist.new_item", icon='ZOOMIN', text="")
                col.operator("arm_traitparamslist.delete_item", icon='ZOOMOUT', text="")

                if len(item.arm_traitparamslist) > 1:
                    col.separator()
                    col.operator("arm_traitparamslist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("arm_traitparamslist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if item.arm_traitparamslist_index >= 0 and len(item.arm_traitparamslist) > 0:
                    paramitem = item.arm_traitparamslist[item.arm_traitparamslist_index]   

                if item.type_prop == 'Haxe Script':
                    row = layout.row(align=True)
                    row.alignment = 'EXPAND'
                    column = row.column(align=True)
                    column.alignment = 'EXPAND'
                    if item.class_name_prop == '':
                        column.enabled = False
                    column.operator("arm.edit_script")
                    row.operator("arm.new_script")
                    row.operator("arm.refresh_scripts")
                else: # Bundled
                    layout.operator("arm.edit_bundled_script")
            
            # JS Script
            elif item.type_prop == 'JS Script':
                item.name = item.jsscript_prop
                row = layout.row()
                row.prop_search(item, "jsscript_prop", bpy.data, "texts", "Text")

            # UI
            elif item.type_prop == 'UI Canvas':
                item.name = item.canvas_name_prop
                row = layout.row()
                row.prop_search(item, "canvas_name_prop", bpy.data.worlds['Arm'], "arm_canvas_list", "Canvas")
                
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                column = row.column(align=True)
                column.alignment = 'EXPAND'
                if item.canvas_name_prop == '':
                    column.enabled = False
                column.operator("arm.edit_canvas")
                row.operator("arm.new_canvas")
                row.operator("arm.refresh_canvas_list")

            # Nodes
            elif item.type_prop == 'Logic Nodes':
                item.name = item.nodes_name_prop
                row = layout.row()
                row.prop_search(item, "nodes_name_prop", bpy.data, "node_groups", "Tree")

def register():  
    bpy.utils.register_class(ArmTraitListItem)
    bpy.utils.register_class(ArmTraitList)
    bpy.utils.register_class(ArmTraitListNewItem)
    bpy.utils.register_class(ArmTraitListDeleteItem)
    bpy.utils.register_class(ArmTraitListMoveItem)
    bpy.utils.register_class(ArmEditScriptButton)
    bpy.utils.register_class(ArmEditBundledScriptButton)
    bpy.utils.register_class(ArmEditCanvasButton)
    bpy.utils.register_class(ArmNewScriptDialog)
    bpy.utils.register_class(ArmNewCanvasDialog)
    bpy.utils.register_class(ArmRefreshScriptsButton)
    bpy.utils.register_class(ArmRefreshCanvasListButton)
    bpy.utils.register_class(ArmTraitsPanel)
    bpy.types.Object.arm_traitlist = bpy.props.CollectionProperty(type=ArmTraitListItem)
    bpy.types.Object.arm_traitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

    # Deprecated
    bpy.utils.register_class(ListTraitItem)
    bpy.types.Object.my_traitlist = bpy.props.CollectionProperty(type=ListTraitItem)

def unregister():
    bpy.utils.unregister_class(ArmTraitListItem)
    bpy.utils.unregister_class(ArmTraitList)
    bpy.utils.unregister_class(ArmTraitListNewItem)
    bpy.utils.unregister_class(ArmTraitListDeleteItem)
    bpy.utils.unregister_class(ArmTraitListMoveItem)
    bpy.utils.unregister_class(ArmEditScriptButton)
    bpy.utils.unregister_class(ArmEditBundledScriptButton)
    bpy.utils.unregister_class(ArmEditCanvasButton)
    bpy.utils.unregister_class(ArmNewScriptDialog)
    bpy.utils.unregister_class(ArmNewCanvasDialog)
    bpy.utils.unregister_class(ArmRefreshScriptsButton)
    bpy.utils.unregister_class(ArmRefreshCanvasListButton)
    bpy.utils.unregister_class(ArmTraitsPanel)

    # Deprecated
    bpy.utils.unregister_class(ListTraitItem)
