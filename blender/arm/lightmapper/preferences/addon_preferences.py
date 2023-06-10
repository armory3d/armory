import bpy, platform
from os.path import basename, dirname
from bpy.types import AddonPreferences
from bpy.props import *
from .. operators import installopencv
from . import addon_preferences
import importlib

class TLM_AddonPreferences(AddonPreferences):

    bl_idname = __name__.split(".")[0]

    tlm_ui_mode: EnumProperty(
        items=[('simple', 'Simple', 'Simple UI'),
               ('advanced', 'Advanced', 'Advanced UI')],
        name='UI mode', default='simple', description='Choose UI mode')

    def draw(self, context):

        layout = self.layout

        box = layout.box()
        row = box.row()

        row.label(text="UI Mode")
        row.prop(self, "tlm_ui_mode")
        row = box.row()
        row.label(text="Simple: Only the basic setup for Blender/Eevee baking with non-experimental features.")
        row = box.row()
        row.label(text="Full set of options available.")
        row = box.row()

        row.label(text="OpenCV")

        cv2 = importlib.util.find_spec("cv2")

        if cv2 is not None:
            row.label(text="OpenCV installed")
        else:
            if platform.system() == "Windows":
                row.label(text="OpenCV not found - Install as administrator!", icon_value=2)
            else:
                row.label(text="OpenCV not found - Click to install!", icon_value=2)
            row = box.row()
            row.operator("tlm.install_opencv_lightmaps", icon="PREFERENCES")

        box = layout.box()
        row = box.row()
        row.label(text="Blender Xatlas")
        if "blender_xatlas" in bpy.context.preferences.addons.keys():
            row.label(text="Blender Xatlas installed and available")
        else:
            row.label(text="Blender Xatlas not installed", icon_value=2)
        row = box.row()
        row.label(text="Github: https://github.com/mattedicksoncom/blender-xatlas")

        box = layout.box()
        row = box.row()
        row.label(text="RizomUV Bridge")
        row.label(text="Coming soon")

        box = layout.box()
        row = box.row()
        row.label(text="UVPackmaster")
        row.label(text="Coming soon")

        uvpacker_addon = False
        for addon in bpy.context.preferences.addons.keys():
            if addon.startswith("UV-Packer"):
                uvpacker_addon = True

        box = layout.box()
        row = box.row()
        row.label(text="UV Packer")
        if uvpacker_addon:
            row.label(text="UV Packer installed and available")
        else:
            row.label(text="UV Packer not installed", icon_value=2)
        row = box.row()
        row.label(text="Github: https://www.uv-packer.com/blender/")

        texel_density_addon = False
        for addon in bpy.context.preferences.addons.keys():
            if addon.startswith("Texel_Density"):
                texel_density_addon = True

        box = layout.box()
        row = box.row()
        row.label(text="Texel Density Checker")
        if texel_density_addon:
            row.label(text="Texel Density Checker installed and available")
        else:
            row.label(text="Texel Density Checker", icon_value=2)
            row.label(text="Coming soon")
        row = box.row()
        row.label(text="Github: https://github.com/mrven/Blender-Texel-Density-Checker")

        box = layout.box()
        row = box.row()
        row.label(text="LuxCoreRender")
        row.label(text="Coming soon")

        box = layout.box()
        row = box.row()
        row.label(text="OctaneRender")
        row.label(text="Coming soon")