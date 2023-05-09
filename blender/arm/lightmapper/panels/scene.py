import bpy, importlib, math
from bpy.props import *
from bpy.types import Menu, Panel
from .. utility import icon
from .. properties.denoiser import oidn, optix

class TLM_PT_Panel(bpy.types.Panel):
    bl_label = "The Lightmapper"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties

class TLM_PT_Groups(bpy.types.Panel):
    bl_label = "Lightmap Groups"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "TLM_PT_Panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            rows = 2
            #if len(atlasList) > 1:
            #    rows = 4

            row = layout.row(align=True)
            row.label(text="Lightmap Group List")
            row = layout.row(align=True)
            row.template_list("TLM_UL_GroupList", "Lightmap Groups", scene, "TLM_GroupList", scene, "TLM_GroupListItem", rows=rows)
            col = row.column(align=True)
            col.operator("tlm_atlaslist.new_item", icon='ADD', text="")
            #col.operator("tlm_atlaslist.delete_item", icon='REMOVE', text="")
            #col.menu("TLM_MT_AtlasListSpecials", icon='DOWNARROW_HLT', text="")

class TLM_PT_Settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties

        row = layout.row(align=True)

        #We list LuxCoreRender as available, by default we assume Cycles exists
        row.prop(sceneProperties, "tlm_lightmap_engine")

        if sceneProperties.tlm_lightmap_engine == "Cycles":

            #CYCLES SETTINGS HERE
            engineProperties = scene.TLM_EngineProperties

            row = layout.row(align=True)
            row.label(text="General Settings")
            row = layout.row(align=True)
            row.operator("tlm.build_lightmaps")
            row = layout.row(align=True)
            row.operator("tlm.clean_lightmaps")
            row = layout.row(align=True)
            row.operator("tlm.explore_lightmaps")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_apply_on_unwrap")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_headless")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_alert_on_finish")

            if sceneProperties.tlm_alert_on_finish:
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_alert_sound")

            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_verbose")
            #row = layout.row(align=True)
            #row.prop(sceneProperties, "tlm_compile_statistics")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_override_bg_color")
            if sceneProperties.tlm_override_bg_color:
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_override_color")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_reset_uv")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_apply_modifiers")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_keep_baked_files")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_repartition_on_clean")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_save_preprocess_lightmaps")

            row = layout.row(align=True)
            try:
                if bpy.context.scene["TLM_Buildstat"] is not None:
                    row.label(text="Last build completed in: " + str(bpy.context.scene["TLM_Buildstat"][0]))
            except:
                pass
            
            row = layout.row(align=True)
            row.label(text="Cycles Settings")

            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_mode")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_quality")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_resolution_scale")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_bake_mode")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_target")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_lighting_mode")
            # if scene.TLM_EngineProperties.tlm_lighting_mode == "combinedao" or scene.TLM_EngineProperties.tlm_lighting_mode == "indirectao":
            #     row = layout.row(align=True)
            #     row.prop(engineProperties, "tlm_premultiply_ao")
            if scene.TLM_EngineProperties.tlm_bake_mode == "Background":
                row = layout.row(align=True)
                row.label(text="Warning! Background mode is currently unstable", icon_value=2)
                row = layout.row(align=True)
                row.prop(sceneProperties, "tlm_network_render")
                if sceneProperties.tlm_network_render:
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_network_paths")
                    #row = layout.row(align=True)
                    #row.prop(sceneProperties, "tlm_network_dir")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_caching_mode")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_directional_mode")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_lightmap_savedir")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_dilation_margin")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_exposure_multiplier")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_setting_supersample")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_metallic_clamp")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_texture_interpolation")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_texture_extrapolation")

        
        
        # elif sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

        #     engineProperties = scene.TLM_Engine2Properties
        #     row = layout.row(align=True)
        #     row.prop(engineProperties, "tlm_luxcore_dir")
        #     row = layout.row(align=True)
        #     row.operator("tlm.build_lightmaps")
        #     #LUXCORE SETTINGS HERE
        #     #luxcore_available = False

        #     #Look for Luxcorerender in the renderengine classes
        #     # for engine in bpy.types.RenderEngine.__subclasses__():
        #     #     if engine.bl_idname == "LUXCORE":
        #     #         luxcore_available = True
        #     #         break

        #     # row = layout.row(align=True)
        #     # if not luxcore_available:
        #     #     row.label(text="Please install BlendLuxCore.")
        #     # else:
        #     #     row.label(text="LuxCoreRender not yet available.")

        elif sceneProperties.tlm_lightmap_engine == "OctaneRender":

            engineProperties = scene.TLM_Engine3Properties

            #LUXCORE SETTINGS HERE
            octane_available = True

            

            row = layout.row(align=True)
            row.operator("tlm.build_lightmaps")
            row = layout.row(align=True)
            row.operator("tlm.clean_lightmaps")
            row = layout.row(align=True)
            row.operator("tlm.explore_lightmaps")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_verbose")
            row = layout.row(align=True)
            row.prop(engineProperties, "tlm_lightmap_savedir")
            row = layout.row(align=True)

class TLM_PT_Denoise(bpy.types.Panel):
    bl_label = "Denoise"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw_header(self, context):
        scene = context.scene
        sceneProperties = scene.TLM_SceneProperties
        self.layout.prop(sceneProperties, "tlm_denoise_use", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties
        layout.active = sceneProperties.tlm_denoise_use

        row = layout.row(align=True)

        #row.prop(sceneProperties, "tlm_denoiser", expand=True)
        #row = layout.row(align=True)
        row.prop(sceneProperties, "tlm_denoise_engine", expand=True)
        row = layout.row(align=True)

        if sceneProperties.tlm_denoise_engine == "Integrated":
            row.label(text="No options for Integrated.")
        elif sceneProperties.tlm_denoise_engine == "OIDN":
            denoiseProperties = scene.TLM_OIDNEngineProperties
            row.prop(denoiseProperties, "tlm_oidn_path")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_oidn_verbose")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_oidn_threads")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_oidn_maxmem")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_oidn_affinity")
            # row = layout.row(align=True)
            # row.prop(denoiseProperties, "tlm_denoise_ao")
        elif sceneProperties.tlm_denoise_engine == "Optix":
            denoiseProperties = scene.TLM_OptixEngineProperties
            row.prop(denoiseProperties, "tlm_optix_path")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_optix_verbose")
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_optix_maxmem")
            #row = layout.row(align=True)
            #row.prop(denoiseProperties, "tlm_denoise_ao")

class TLM_PT_Filtering(bpy.types.Panel):
    bl_label = "Filtering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw_header(self, context):
        scene = context.scene
        sceneProperties = scene.TLM_SceneProperties
        self.layout.prop(sceneProperties, "tlm_filtering_use", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties
        layout.active = sceneProperties.tlm_filtering_use
        #row = layout.row(align=True)
        #row.label(text="TODO MAKE CHECK")
        #row = layout.row(align=True)
        #row.prop(sceneProperties, "tlm_filtering_engine", expand=True)
        row = layout.row(align=True)

        if sceneProperties.tlm_filtering_engine == "OpenCV":

            cv2 = importlib.util.find_spec("cv2")

            if cv2 is None:
                row = layout.row(align=True)
                row.label(text="OpenCV is not installed. Install it through preferences.")
            else:
                row = layout.row(align=True)
                row.prop(scene.TLM_SceneProperties, "tlm_filtering_mode")
                row = layout.row(align=True)
                if scene.TLM_SceneProperties.tlm_filtering_mode == "Gaussian":
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_gaussian_strength")
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
                elif scene.TLM_SceneProperties.tlm_filtering_mode == "Box":
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_box_strength")
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")

                elif scene.TLM_SceneProperties.tlm_filtering_mode == "Bilateral":
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_diameter")
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_color_deviation")
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_bilateral_coordinate_deviation")
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
                else:
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_median_kernel", expand=True)
                    row = layout.row(align=True)
                    row.prop(scene.TLM_SceneProperties, "tlm_filtering_iterations")
        else:
            row = layout.row(align=True)
            row.prop(scene.TLM_SceneProperties, "tlm_numpy_filtering_mode")


class TLM_PT_Encoding(bpy.types.Panel):
    bl_label = "Encoding"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw_header(self, context):
        scene = context.scene
        sceneProperties = scene.TLM_SceneProperties
        self.layout.prop(sceneProperties, "tlm_encoding_use", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties
        layout.active = sceneProperties.tlm_encoding_use

        sceneProperties = scene.TLM_SceneProperties
        row = layout.row(align=True)

        if scene.TLM_EngineProperties.tlm_bake_mode == "Background":
            row.label(text="Encoding options disabled in background mode")
            row = layout.row(align=True)

        else:

            row.prop(sceneProperties, "tlm_encoding_device", expand=True)
            row = layout.row(align=True)

            if sceneProperties.tlm_encoding_device == "CPU":
                row.prop(sceneProperties, "tlm_encoding_mode_a", expand=True)
            else:
                row.prop(sceneProperties, "tlm_encoding_mode_b", expand=True)

            if sceneProperties.tlm_encoding_device == "CPU":
                if sceneProperties.tlm_encoding_mode_a == "RGBM":
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_encoding_range")
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_decoder_setup")
                if sceneProperties.tlm_encoding_mode_a == "RGBD":
                    pass
                if sceneProperties.tlm_encoding_mode_a == "HDR":
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_format")
            else:

                if sceneProperties.tlm_encoding_mode_b == "RGBM":
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_encoding_range")
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_decoder_setup")

                if sceneProperties.tlm_encoding_mode_b == "LogLuv" and sceneProperties.tlm_encoding_device == "GPU":
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_decoder_setup")
                    if sceneProperties.tlm_decoder_setup:
                        row = layout.row(align=True)
                        row.prop(sceneProperties, "tlm_split_premultiplied")
                if sceneProperties.tlm_encoding_mode_b == "HDR":
                    row = layout.row(align=True)
                    row.prop(sceneProperties, "tlm_format")

class TLM_PT_Utility(bpy.types.Panel):
    bl_label = "Utilities"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties

        row = layout.row(align=True)
        row.label(text="Enable Lightmaps for set")
        row = layout.row(align=True)
        row.prop(sceneProperties, "tlm_utility_context")
        row = layout.row(align=True)

        if sceneProperties.tlm_utility_context == "SetBatching":

            row.operator("tlm.enable_set")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_utility_set")
            row = layout.row(align=True)
            #row.label(text="ABCD")
            row.prop(sceneProperties, "tlm_mesh_lightmap_unwrap_mode")

            if sceneProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                if scene.TLM_AtlasListItem >= 0 and len(scene.TLM_AtlasList) > 0:
                    row = layout.row()
                    item = scene.TLM_AtlasList[scene.TLM_AtlasListItem]
                    row.prop_search(sceneProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                else:
                    row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")

            else:

                row = layout.row()
                row.prop(sceneProperties, "tlm_postpack_object")
                row = layout.row()
            
                if sceneProperties.tlm_postpack_object and sceneProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":

                    if scene.TLM_PostAtlasListItem >= 0 and len(scene.TLM_PostAtlasList) > 0:
                        row = layout.row()
                        item = scene.TLM_PostAtlasList[scene.TLM_PostAtlasListItem]
                        row.prop_search(sceneProperties, "tlm_postatlas_pointer", scene, "TLM_PostAtlasList", text='Atlas Group')
                        row = layout.row()

                    else:
                        row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                        row = layout.row()

                row.prop(sceneProperties, "tlm_mesh_unwrap_margin")
                row = layout.row()
                row.prop(sceneProperties, "tlm_resolution_weight")

                if sceneProperties.tlm_resolution_weight == "Single":
                    row = layout.row()
                    row.prop(sceneProperties, "tlm_mesh_lightmap_resolution")
                else:
                    row = layout.row()
                    row.prop(sceneProperties, "tlm_resolution_min")
                    row = layout.row()
                    row.prop(sceneProperties, "tlm_resolution_max")

            row = layout.row()
            row.operator("tlm.disable_selection")
            row = layout.row(align=True)
            row.operator("tlm.select_lightmapped_objects")
            row = layout.row(align=True)
            row.operator("tlm.remove_uv_selection")
        
        elif sceneProperties.tlm_utility_context == "EnvironmentProbes":

            row.label(text="Environment Probes")
            row = layout.row()
            row.operator("tlm.build_environmentprobe")
            row = layout.row()
            row.operator("tlm.clean_environmentprobe")
            row = layout.row()
            row.prop(sceneProperties, "tlm_environment_probe_engine")
            row = layout.row()
            row.prop(sceneProperties, "tlm_cmft_path")
            row = layout.row()
            row.prop(sceneProperties, "tlm_environment_probe_resolution")
            row = layout.row()
            row.prop(sceneProperties, "tlm_create_spherical")

            if sceneProperties.tlm_create_spherical:

                row = layout.row()
                row.prop(sceneProperties, "tlm_invert_direction")
                row = layout.row()
                row.prop(sceneProperties, "tlm_write_sh")
                row = layout.row()
                row.prop(sceneProperties, "tlm_write_radiance")

        elif sceneProperties.tlm_utility_context == "LoadLightmaps":

            row = layout.row(align=True)
            row.label(text="Load lightmaps")
            row = layout.row()
            row.prop(sceneProperties, "tlm_load_folder")
            row = layout.row()
            row.operator("tlm.load_lightmaps")
            row = layout.row()
            row.prop(sceneProperties, "tlm_load_atlas")

        elif sceneProperties.tlm_utility_context == "MaterialAdjustment":
        
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_utility_set")
            row = layout.row(align=True)
            row.operator("tlm.disable_specularity")
            row.operator("tlm.disable_metallic")
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_remove_met_spec_link")
            row = layout.row(align=True)
            row.operator("tlm.remove_empty_images")
            row = layout.row(align=True)

        elif sceneProperties.tlm_utility_context == "NetworkRender":

            row.label(text="Network Rendering")
            row = layout.row()
            row.operator("tlm.start_server")
            layout.label(text="Atlas Groups")

        elif sceneProperties.tlm_utility_context == "TexelDensity":

            row.label(text="Texel Density Utilies")
            row = layout.row()

        elif sceneProperties.tlm_utility_context == "GLTFUtil":

            row.label(text="GLTF material utilities")
            row = layout.row()
            row.operator("tlm.add_gltf_node")
            row = layout.row()
            row.operator("tlm.shift_multiply_links")

class TLM_PT_Selection(bpy.types.Panel):
    bl_label = "Selection"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        sceneProperties = scene.TLM_SceneProperties

        row = layout.row(align=True)
        row.operator("tlm.enable_selection")
        row = layout.row(align=True)
        row.operator("tlm.disable_selection")
        row = layout.row(align=True)
        row.prop(sceneProperties, "tlm_override_object_settings")

        if sceneProperties.tlm_override_object_settings:

            row = layout.row(align=True)
            row = layout.row()
            row.prop(sceneProperties, "tlm_mesh_lightmap_unwrap_mode")
            row = layout.row()

            if sceneProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":

                if scene.TLM_AtlasListItem >= 0 and len(scene.TLM_AtlasList) > 0:
                    row = layout.row()
                    item = scene.TLM_AtlasList[scene.TLM_AtlasListItem]
                    row.prop_search(sceneProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                else:
                    row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")

            else:
                row = layout.row()
                row.prop(sceneProperties, "tlm_postpack_object")
                row = layout.row()

            if sceneProperties.tlm_postpack_object and sceneProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                if scene.TLM_PostAtlasListItem >= 0 and len(scene.TLM_PostAtlasList) > 0:
                    row = layout.row()
                    item = scene.TLM_PostAtlasList[scene.TLM_PostAtlasListItem]
                    row.prop_search(sceneProperties, "tlm_postatlas_pointer", scene, "TLM_PostAtlasList", text='Atlas Group')
                    row = layout.row()

                else:
                    row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")
                    row = layout.row()

            if sceneProperties.tlm_mesh_lightmap_unwrap_mode != "AtlasGroupA":
                row.prop(sceneProperties, "tlm_mesh_lightmap_resolution")
                row = layout.row()
                row.prop(sceneProperties, "tlm_mesh_unwrap_margin")

        row = layout.row(align=True)
        row.operator("tlm.remove_uv_selection")
        row = layout.row(align=True)
        row.operator("tlm.select_lightmapped_objects")
        # row = layout.row(align=True)
        # for addon in bpy.context.preferences.addons.keys():
        #     if addon.startswith("Texel_Density"):
        #         row.operator("tlm.toggle_texel_density")
        #         row = layout.row(align=True)

class TLM_PT_Additional(bpy.types.Panel):
    bl_label = "Additional"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "ARM_PT_BakePanel"

    @classmethod 
    def poll(self, context):
        scene = context.scene
        return scene.arm_bakemode == "Lightmap"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sceneProperties = scene.TLM_SceneProperties
        atlasListItem = scene.TLM_AtlasListItem
        atlasList = scene.TLM_AtlasList
        postatlasListItem = scene.TLM_PostAtlasListItem
        postatlasList = scene.TLM_PostAtlasList

        row = layout.row()
        row.prop(sceneProperties, "tlm_atlas_mode", expand=True)

        if sceneProperties.tlm_atlas_mode == "Prepack":

            rows = 2
            if len(atlasList) > 1:
                rows = 4
            row = layout.row()
            row.template_list("TLM_UL_AtlasList", "Atlas List", scene, "TLM_AtlasList", scene, "TLM_AtlasListItem", rows=rows)
            col = row.column(align=True)
            col.operator("tlm_atlaslist.new_item", icon='ADD', text="")
            col.operator("tlm_atlaslist.delete_item", icon='REMOVE', text="")
            col.menu("TLM_MT_AtlasListSpecials", icon='DOWNARROW_HLT', text="")

            if atlasListItem >= 0 and len(atlasList) > 0:
                item = atlasList[atlasListItem]
                layout.prop(item, "tlm_atlas_lightmap_unwrap_mode")
                layout.prop(item, "tlm_atlas_lightmap_resolution")
                layout.prop(item, "tlm_atlas_unwrap_margin")

                amount = 0

                for obj in bpy.context.scene.objects:
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                            if obj.TLM_ObjectProperties.tlm_atlas_pointer == item.name:
                                amount = amount + 1

                layout.label(text="Objects: " + str(amount))
                layout.prop(item, "tlm_atlas_merge_samemat")

                layout.prop(item, "tlm_use_uv_packer")
                layout.prop(item, "tlm_uv_packer_padding")
                layout.prop(item, "tlm_uv_packer_packing_engine")

        else:

            layout.label(text="Postpacking is unstable.")

            cv2 = importlib.util.find_spec("cv2")

            if cv2 is None:

                row = layout.row(align=True)
                row.label(text="OpenCV is not installed. Install it through preferences.")

            else:

                rows = 2
                if len(atlasList) > 1:
                    rows = 4
                row = layout.row()
                row.template_list("TLM_UL_PostAtlasList", "PostList", scene, "TLM_PostAtlasList", scene, "TLM_PostAtlasListItem", rows=rows)
                col = row.column(align=True)
                col.operator("tlm_postatlaslist.new_item", icon='ADD', text="")
                col.operator("tlm_postatlaslist.delete_item", icon='REMOVE', text="")
                col.menu("TLM_MT_PostAtlasListSpecials", icon='DOWNARROW_HLT', text="")

                if postatlasListItem >= 0 and len(postatlasList) > 0:
                    item = postatlasList[postatlasListItem]
                    layout.prop(item, "tlm_atlas_lightmap_resolution")

                    #Below list object counter
                    amount = 0
                    utilized = 0
                    atlasUsedArea = 0
                    atlasSize = item.tlm_atlas_lightmap_resolution

                    for obj in bpy.context.scene.objects:
                        if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                            if obj.TLM_ObjectProperties.tlm_postpack_object:
                                if obj.TLM_ObjectProperties.tlm_postatlas_pointer == item.name:
                                    amount = amount + 1
                                    
                                    atlasUsedArea += int(obj.TLM_ObjectProperties.tlm_mesh_lightmap_resolution) ** 2

                    row = layout.row()
                    row.prop(item, "tlm_atlas_repack_on_cleanup")

                    #TODO SET A CHECK FOR THIS! ADD A CV2 CHECK TO UTILITY!
                    cv2 = True

                    if cv2:
                        row = layout.row()
                        row.prop(item, "tlm_atlas_dilation")
                    layout.label(text="Objects: " + str(amount))

                    utilized = atlasUsedArea / (int(atlasSize) ** 2)
                    layout.label(text="Utilized: " + str(utilized * 100) + "%")

                    if (utilized * 100) > 100:
                        layout.label(text="Warning! Overflow not yet supported")
