import bpy, os, math, importlib

from bpy.types import Menu, Operator, Panel, UIList

from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)

class TLM_PT_Imagetools(bpy.types.Panel):
    bl_label = "TLM Imagetools"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = 'UI'
    bl_category = "TLM Imagetools"

    def draw_header(self, _):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text ="Image Tools")

    def draw(self, context):
        layout = self.layout

        activeImg = None

        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                activeImg = area.spaces.active.image

        if activeImg is not None and activeImg.name != "Render Result" and activeImg.name != "Viewer Node":

            cv2 = importlib.util.find_spec("cv2")

            if cv2 is None:
                row = layout.row(align=True)
                row.label(text ="OpenCV not installed.")
            else:

                row = layout.row(align=True)
                row.label(text ="Method")
                row = layout.row(align=True)
                row.prop(activeImg.TLM_ImageProperties, "tlm_image_scale_engine")
                row = layout.row(align=True)
                row.prop(activeImg.TLM_ImageProperties, "tlm_image_cache_switch")
                row = layout.row(align=True)
                row.operator("tlm.image_upscale")
                if activeImg.TLM_ImageProperties.tlm_image_cache_switch:
                    row = layout.row(align=True)
                    row.label(text ="Switch up.")
                row = layout.row(align=True)
                row.operator("tlm.image_downscale")
                if activeImg.TLM_ImageProperties.tlm_image_cache_switch:
                    row = layout.row(align=True)
                    row.label(text ="Switch down.")
                if activeImg.TLM_ImageProperties.tlm_image_scale_engine == "OpenCV":
                    row = layout.row(align=True)
                    row.prop(activeImg.TLM_ImageProperties, "tlm_image_scale_method")

        else:
            row = layout.row(align=True)
            row.label(text ="Select an image")