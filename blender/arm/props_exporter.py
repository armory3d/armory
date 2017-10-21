import os
import shutil
import arm.assets as assets
import arm.make_utils as make_utils
import bpy
import stat
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update_gapi_win(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/windows-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/windows-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_winapp(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/windowsapp-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/windowsapp-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_linux(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/linux-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/linux-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_mac(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/osx-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/osx-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_android(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/android-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/android-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_ios(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/ios-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/ios-build', onerror=remove_readonly)
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_html5(self, context):
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

class ArmExporterListItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="Preset")

    arm_project_rp = bpy.props.StringProperty(
           name="Render Path",
           description="A name for this item",
           default="Path")

    arm_project_target = EnumProperty(
        items = [('html5', 'HTML5', 'html5'),
                 ('windows', 'Windows', 'windows'),
                 ('windowsapp', 'WindowsApp', 'windowsapp'),
                 ('macos', 'MacOS', 'macos'),
                 ('linux', 'Linux', 'linux'),
                 ('ios', 'iOS', 'ios'),
                 ('android-native', 'Android', 'android-native'),
                 ('krom', 'Krom', 'krom'),
                 ('node', 'Node', 'node')],
        name="Target", default='html5', description='Build paltform')

    arm_gapi_win = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan'),
                 ('direct3d9', 'Direct3D9', 'direct3d9'),
                 ('direct3d11', 'Direct3D11', 'direct3d11'),
                 ('direct3d12', 'Direct3D12', 'direct3d12')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_win)
    arm_gapi_winapp = EnumProperty(
        items = [('direct3d11', 'Auto', 'direct3d11'),
                 ('direct3d11', 'Direct3D11', 'direct3d11')],
        name="Graphics API", default='direct3d11', description='Based on currently selected target', update=update_gapi_winapp)
    arm_gapi_linux = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_linux)
    arm_gapi_android = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_android)
    arm_gapi_mac = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('metal', 'Metal', 'metal')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_mac)
    arm_gapi_ios = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('metal', 'Metal', 'metal')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_ios)
    arm_gapi_html5 = EnumProperty(
        items = [('webgl', 'Auto', 'webgl'),
                 ('webgl', 'WebGL', 'webgl')],
        name="Graphics API", default='webgl', description='Based on currently selected target', update=update_gapi_html5)

class ArmExporterList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(item.arm_project_target)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon = custom_icon)

class ArmExporterListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_exporterlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        mdata.arm_exporterlist.add()
        mdata.arm_exporterlist_index = len(mdata.arm_exporterlist) - 1
        return{'FINISHED'}


class ArmExporterListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_exporterlist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.data.worlds['Arm']
        return len(mdata.arm_exporterlist) > 0

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_exporterlist
        index = mdata.arm_exporterlist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_exporterlist_index = index
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmExporterListItem)
    bpy.utils.register_class(ArmExporterList)
    bpy.utils.register_class(ArmExporterListNewItem)
    bpy.utils.register_class(ArmExporterListDeleteItem)

    bpy.types.World.arm_exporterlist = bpy.props.CollectionProperty(type=ArmExporterListItem)
    bpy.types.World.arm_exporterlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)

def unregister():
    bpy.utils.unregister_class(ArmExporterListItem)
    bpy.utils.unregister_class(ArmExporterList)
    bpy.utils.unregister_class(ArmExporterListNewItem)
    bpy.utils.unregister_class(ArmExporterListDeleteItem)
