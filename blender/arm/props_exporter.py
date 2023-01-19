import os
import shutil
import stat
import subprocess
import webbrowser

import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

import arm.assets as assets
import arm.utils
import arm.utils_vs

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    arm.utils = arm.reload_module(arm.utils)
    arm.utils_vs = arm.reload_module(arm.utils_vs)
else:
    arm.enable_reload(__name__)


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update_gapi_custom(self, context):
    bpy.data.worlds['Arm'].arm_recompile = True
    assets.invalidate_compiled_data(self, context)

def update_gapi_win(self, context):
    if os.path.isdir(arm.utils.get_fp_build() + '/windows-build'):
        shutil.rmtree(arm.utils.get_fp_build() + '/windows-build', onerror=remove_readonly)
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
    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="Preset")

    arm_project_rp: StringProperty(
           name="Render Path",
           description="A name for this item",
           default="")

    arm_project_scene: PointerProperty(
            name="Scene",
            description="Scene to load when launching",
            type=bpy.types.Scene)

    arm_project_target: EnumProperty(
        items = [('html5', 'HTML5 (JS)', 'html5'),
                 ('windows-hl', 'Windows (C)', 'windows-hl'),
                 ('krom-windows', 'Windows (Krom)', 'krom-windows'),
                 ('macos-hl', 'macOS (C)', 'macos-hl'),
                 ('krom-macos', 'macOS (Krom)', 'krom-macos'),
                 ('linux-hl', 'Linux (C)', 'linux-hl'),
                 ('krom-linux', 'Linux (Krom)', 'krom-linux'),
                 ('ios-hl', 'iOS (C)', 'ios-hl'),
                 ('android-hl', 'Android (C)', 'android-hl'),
                 ('node', 'Node (JS)', 'node'),
                 ('custom', 'Custom', 'custom'),],
        name="Target", default='html5', description='Build platform')

    arm_project_khamake: StringProperty(name="Khamake", description="Specify arguments for the 'node Kha/make' call")

    arm_gapi_custom: EnumProperty(
        items = [('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan'),
                 ('direct3d11', 'Direct3D11', 'direct3d11'),
                 ('direct3d12', 'Direct3D12', 'direct3d12'),
                 ('metal', 'Metal', 'metal')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_custom)
    arm_gapi_win: EnumProperty(
        items = [('direct3d11', 'Auto', 'direct3d11'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan'),
                 ('direct3d11', 'Direct3D11', 'direct3d11'),
                 ('direct3d12', 'Direct3D12', 'direct3d12')],
        name="Graphics API", default='direct3d11', description='Based on currently selected target', update=update_gapi_win)
    arm_gapi_linux: EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_linux)
    arm_gapi_android: EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('vulkan', 'Vulkan', 'vulkan')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_android)
    arm_gapi_mac: EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('metal', 'Metal', 'metal')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_mac)
    arm_gapi_ios: EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('metal', 'Metal', 'metal')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_ios)
    arm_gapi_html5: EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'WebGL2', 'opengl')],
        name="Graphics API", default='opengl', description='Based on currently selected target', update=update_gapi_html5)

class ArmExporterAndroidPermissionListItem(bpy.types.PropertyGroup):
    arm_android_permissions: EnumProperty(
        items = [('ACCESS_COARSE_LOCATION ', 'Access Coarse Location', 'Allows an app to access approximate location'),
                 ('ACCESS_NETWORK_STATE', 'Access Network State', 'Allows applications to access information about networks'),
                 ('ACCESS_FINE_LOCATION', 'Access Fine Location', 'Allows an app to access precise location'),
                 ('ACCESS_WIFI_STATE', 'Access Wi-Fi State', 'Allows applications to access information about Wi-Fi networks'),
                 ('BLUETOOTH', 'Bluetooth', 'Allows applications to connect to paired bluetooth devices'),
                 ('BLUETOOTH_ADMIN', 'Bluetooth Admin', 'Allows applications to discover and pair bluetooth devices'),
                 ('CAMERA', 'Camera', 'Required to be able to access the camera device'),
                 ('EXPAND_STATUS_BAR', 'Expand Status Bar', 'Allows an application to expand or collapse the status bar'),
                 ('FOREGROUND_SERVICE', 'Foreground Service', 'Allows a regular application to use Service.startForeground'),
                 ('GET_ACCOUNTS', 'Get Accounts', 'Allows access to the list of accounts in the Accounts Service'),
                 ('INTERNET', 'Internet', 'Allows applications to open network sockets'),
                 ('READ_EXTERNAL_STORAGE', 'Read External Storage', 'Allows an application to read from external storage.'),
                 ('VIBRATE', 'Vibrate', 'Allows access to the vibrator'),
                 ('WRITE_EXTERNAL_STORAGE', 'Write External Storage', 'Allows an application to write to external storage')],
        name="Permission", default='VIBRATE', description='Android Permission')

class ArmExporterAndroidAbiListItem(bpy.types.PropertyGroup):
    arm_android_abi: EnumProperty(
        items = [('arm64-v8a', 'arm64-v8a', 'This ABI is for ARMv8-A based CPUs, which support the 64-bit AArch64 architecture'),
                 ('armeabi-v7a', 'armeabi-v7a', 'This ABI is for 32-bit ARM-based CPUs'),
                 ('x86', 'x86', 'This ABI is for CPUs supporting the instruction set commonly known as x86, i386, or IA-32'),
                 ('x86_64', 'x86_64', 'This ABI is for CPUs supporting the instruction set commonly referred to as x86-64')],
        name="Android ABI", default='arm64-v8a', description='Android ABI')

class ARM_UL_ExporterList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'DOT'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text=item.arm_project_target)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ARM_UL_Exporter_AndroidPermissionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'DOT'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text=item.arm_android_permissions)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ARM_UL_Exporter_AndroidAbiList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'DOT'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text=item.arm_android_abi)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class ArmExporterListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_exporterlist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        mdata.arm_exporterlist.add()
        mdata.arm_exporterlist_index = len(mdata.arm_exporterlist) - 1
        if len(mdata.arm_rplist) > mdata.arm_exporterlist_index:
            mdata.arm_exporterlist[-1].arm_project_rp = mdata.arm_rplist[mdata.arm_rplist_index].name
        mdata.arm_exporterlist[-1].arm_project_scene = context.scene
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

class ArmExporterListMoveItem(bpy.types.Operator):
    # Move an item in the list
    bl_idname = "arm_exporterlist.move_item"
    bl_label = "Move an item in the list"
    direction: EnumProperty(
                items=(
                    ('UP', 'Up', ""),
                    ('DOWN', 'Down', ""),))

    def move_index(self):
        # Move index of an item render queue while clamping it
        mdata = bpy.data.worlds['Arm']
        index = mdata.arm_exporterlist_index
        list_length = len(mdata.arm_exporterlist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1

        new_index = max(0, min(new_index, list_length))
        mdata.arm_exporterlist.move(index, new_index)
        mdata.arm_exporterlist_index = new_index

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_exporterlist
        index = mdata.arm_exporterlist_index

        if self.direction == 'DOWN':
            neighbor = index + 1
            self.move_index()

        elif self.direction == 'UP':
            neighbor = index - 1
            self.move_index()
        else:
            return{'CANCELLED'}
        return{'FINISHED'}

class ArmExporter_AndroidPermissionListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_exporter_android_permission_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        mdata.arm_exporter_android_permission_list.add()
        mdata.arm_exporter_android_permission_list_index = len(mdata.arm_exporter_android_permission_list) - 1
        return{'FINISHED'}

class ArmExporter_AndroidPermissionListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_exporter_android_permission_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.data.worlds['Arm']
        return len(mdata.arm_exporter_android_permission_list) > 0

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_exporter_android_permission_list
        index = mdata.arm_exporter_android_permission_list_index

        list.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_exporter_android_permission_list_index = index
        return{'FINISHED'}

class ArmExporter_AndroidAbiListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_exporter_android_abi_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        mdata.arm_exporter_android_abi_list.add()
        mdata.arm_exporter_android_abi_list_index = len(mdata.arm_exporter_android_abi_list) - 1
        return{'FINISHED'}

class ArmExporter_AndroidAbiListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_exporter_android_abi_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        mdata = bpy.data.worlds['Arm']
        return len(mdata.arm_exporter_android_abi_list) > 0

    def execute(self, context):
        mdata = bpy.data.worlds['Arm']
        list = mdata.arm_exporter_android_abi_list
        index = mdata.arm_exporter_android_abi_list_index

        list.remove(index)

        if index > 0:
            index = index - 1

        mdata.arm_exporter_android_abi_list_index = index
        return{'FINISHED'}


class ArmExporterSpecialsMenu(bpy.types.Menu):
    bl_label = "More"
    bl_idname = "ARM_MT_ExporterListSpecials"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.exporter_open_folder")
        layout.operator("arm.exporter_gpuprofile")
        if arm.utils.get_os_is_windows():
            layout.operator("arm.exporter_open_vs")


class ArmoryExporterOpenFolderButton(bpy.types.Operator):
    """Open published folder"""
    bl_idname = 'arm.exporter_open_folder'
    bl_label = 'Open Folder'

    def execute(self, context):
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_exporterlist) == 0:
            return {'CANCELLED'}
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        p = os.path.join(arm.utils.get_fp_build(), item.arm_project_target)
        if os.path.exists(p):
            webbrowser.open('file://' + p)
        return{'FINISHED'}

class ArmExporterGpuProfileButton(bpy.types.Operator):
    '''GPU profile'''
    bl_idname = 'arm.exporter_gpuprofile'
    bl_label = 'Open in RenderDoc'

    def execute(self, context):
        p = arm.utils.get_renderdoc_path()
        if p == '':
            self.report({'ERROR'}, 'Configure RenderDoc path in Armory add-on preferences')
            return {'CANCELLED'}
        pbin = ''
        base = arm.utils.get_fp_build()
        ext1 =  '/krom-windows/' + arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_name) + '.exe'
        ext2 =  '/krom-linux/' + arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_name)
        if os.path.exists(base + ext1):
            pbin = base + ext1
        elif os.path.exists(base + ext2):
            pbin = base + ext2
        if pbin == '':
            self.report({'ERROR'}, 'Publish project using Krom target first')
            return {'CANCELLED'}
        subprocess.Popen([p, pbin])
        return{'FINISHED'}


class ARM_OT_ExporterOpenVS(bpy.types.Operator):
    """Open the generated project in Visual Studio, if installed"""
    bl_idname = 'arm.exporter_open_vs'
    bl_label = 'Open in Visual Studio'

    @classmethod
    def poll(cls, context):
        if not arm.utils.get_os_is_windows():
            cls.poll_message_set('This operator is only supported on Windows')
            return False

        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_exporterlist) == 0:
            cls.poll_message_set('No export configuration exists')
            return False

        if wrd.arm_exporterlist[wrd.arm_exporterlist_index].arm_project_target != 'windows-hl':
            cls.poll_message_set('This operator only works with the Windows (C) target')
            return False

        return True

    def execute(self, context):
        version_major, version_min_full, err = arm.utils_vs.fetch_project_version()
        if err is not None:
            if err == 'err_file_not_found':
                self.report({'ERROR'}, 'Publish project using Windows (C) target first')
            elif err.startswith('err_invalid_version'):
                self.report({'ERROR'}, 'Could not parse Visual Studio version, check console for details')
            return {'CANCELLED'}

        success = arm.utils_vs.open_project_in_vs(version_major, version_min_full)
        if not success:
            self.report({'ERROR'}, 'Could not open the project in Visual Studio, check console for details')
            return {'CANCELLED'}

        return{'FINISHED'}


REG_CLASSES = (
    ArmExporterListItem,
    ArmExporterAndroidPermissionListItem,
    ArmExporterAndroidAbiListItem,
    ARM_UL_ExporterList,
    ARM_UL_Exporter_AndroidPermissionList,
    ARM_UL_Exporter_AndroidAbiList,
    ArmExporterListNewItem,
    ArmExporterListDeleteItem,
    ArmExporterListMoveItem,
    ArmExporter_AndroidPermissionListNewItem,
    ArmExporter_AndroidPermissionListDeleteItem,
    ArmExporter_AndroidAbiListNewItem,
    ArmExporter_AndroidAbiListDeleteItem,
    ArmExporterSpecialsMenu,
    ArmExporterGpuProfileButton,
    ArmoryExporterOpenFolderButton,
    ARM_OT_ExporterOpenVS
)
_reg_classes, _unreg_classes = bpy.utils.register_classes_factory(REG_CLASSES)


def register():
    _reg_classes()

    bpy.types.World.arm_exporterlist = CollectionProperty(type=ArmExporterListItem)
    bpy.types.World.arm_exporterlist_index = IntProperty(name="Index for my_list", default=0)
    bpy.types.World.arm_exporter_android_permission_list = CollectionProperty(type=ArmExporterAndroidPermissionListItem)
    bpy.types.World.arm_exporter_android_permission_list_index = IntProperty(name="Index for my_list", default=0)
    bpy.types.World.arm_exporter_android_abi_list = CollectionProperty(type=ArmExporterAndroidAbiListItem)
    bpy.types.World.arm_exporter_android_abi_list_index = IntProperty(name="Index for my_list", default=0)


def unregister():
    _unreg_classes()
