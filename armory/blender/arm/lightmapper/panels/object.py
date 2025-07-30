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
                row.prop(obj.TLM_ObjectProperties, "tlm_use_default_channel")

                if not obj.TLM_ObjectProperties.tlm_use_default_channel:

                    row = layout.row()
                    row.prop_search(obj.TLM_ObjectProperties, "tlm_uv_channel", obj.data, "uv_layers", text='UV Channel')

                row = layout.row()
                row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_resolution")
                if obj.TLM_ObjectProperties.tlm_use_default_channel:
                    row = layout.row()
                    row.prop(obj.TLM_ObjectProperties, "tlm_mesh_lightmap_unwrap_mode")
                row = layout.row()
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                    if scene.TLM_AtlasListItem >= 0 and len(scene.TLM_AtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_AtlasList[scene.TLM_AtlasListItem]
                        row.prop_search(obj.TLM_ObjectProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                        row = layout.row()
                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

                else:
                    row = layout.row()
                    row.prop(obj.TLM_ObjectProperties, "tlm_postpack_object")
                    row = layout.row()


                if obj.TLM_ObjectProperties.tlm_postpack_object and obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                    if scene.TLM_PostAtlasListItem >= 0 and len(scene.TLM_PostAtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_PostAtlasList[scene.TLM_PostAtlasListItem]
                        row.prop_search(obj.TLM_ObjectProperties, "tlm_postatlas_pointer", scene, "TLM_PostAtlasList", text='Atlas Group')
                        row = layout.row()

                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

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

                #If UV Packer installed
                if "UV-Packer" in bpy.context.preferences.addons.keys():
                    row.prop(obj.TLM_ObjectProperties, "tlm_use_uv_packer")
                    if obj.TLM_ObjectProperties.tlm_use_uv_packer:
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_uv_packer_padding")
                        row = layout.row(align=True)
                        row.prop(obj.TLM_ObjectProperties, "tlm_uv_packer_packing_engine")

class TLM_PT_MaterialMenu(bpy.types.Panel):
    bl_label = "The Lightmapper"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = bpy.context.object
        layout.use_property_split = True
        layout.use_property_decorate = False

        mat = bpy.context.material
        if mat == None:
            return

        if obj.type == "MESH":

            row = layout.row()
            row.prop(mat, "TLM_ignore")