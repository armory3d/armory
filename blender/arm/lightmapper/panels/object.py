import bpy
from bpy.props import *
from bpy.types import Menu, Panel

class TLM_PT_ObjectMenu(bpy.types.Panel):
    bl_label = "The Lightmapper"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = bpy.context.object
        layout.use_property_split = True
        layout.use_property_decorate = False

        if obj.type == "MESH":
            row = layout.row(align=True)
            row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_use")

            if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:

                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_resolution")
                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_unwrap_mode")
                row = layout.row()
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroup":
                    pass
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_unwrap_margin")
                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filter_override")
                row = layout.row()
                if obj.TLM_ObjectProperties.tlm_mesh_filter_override:
                    row = layout.row(align=True)
                    row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_mode")
                    row = layout.row(align=True)
                    if obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Gaussian":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_gaussian_strength")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    elif obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Box":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_box_strength")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    elif obj.TLM_ObjectProperties.tlm_mesh_filtering_mode == "Bilateral":
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_diameter")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_color_deviation")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_bilateral_coordinate_deviation")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")
                    else:
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_median_kernel", expand=True)
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_mesh_filtering_iterations")