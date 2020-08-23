import bpy, importlib
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

class TLM_PT_Settings(bpy.types.Panel):
    bl_label = "Settings"
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

            if scene.TLM_EngineProperties.tlm_bake_mode == "Background":
                row = layout.row(align=True)
                row.label(text="Warning! Background mode is currently unstable", icon_value=2)
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

        elif sceneProperties.tlm_lightmap_engine == "LuxCoreRender":

            #LUXCORE SETTINGS HERE
            luxcore_available = False

            #Look for Luxcorerender in the renderengine classes
            for engine in bpy.types.RenderEngine.__subclasses__():
                if engine.bl_idname == "LUXCORE":
                    luxcore_available = True
                    break

            row = layout.row(align=True)
            if not luxcore_available:
                row.label(text="Please install BlendLuxCore.")
            else:
                row.label(text="LuxCoreRender not yet available.")

        elif sceneProperties.tlm_lightmap_engine == "OctaneRender":

            #LUXCORE SETTINGS HERE
            octane_available = False

            row = layout.row(align=True)
            row.label(text="Octane Render not yet available.")

class TLM_PT_Denoise(bpy.types.Panel):
    bl_label = "Denoise"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "TLM_PT_Panel"

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
            row = layout.row(align=True)
            row.prop(denoiseProperties, "tlm_denoise_ao")

class TLM_PT_Filtering(bpy.types.Panel):
    bl_label = "Filtering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "TLM_PT_Panel"

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
        row = layout.row(align=True)
        row.prop(sceneProperties, "tlm_filtering_engine", expand=True)
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
    bl_parent_id = "TLM_PT_Panel"

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
        row.prop(sceneProperties, "tlm_encoding_mode", expand=True)
        if sceneProperties.tlm_encoding_mode == "RGBM" or sceneProperties.tlm_encoding_mode == "RGBD":
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_encoding_range")
        if sceneProperties.tlm_encoding_mode == "LogLuv":
            pass
        if sceneProperties.tlm_encoding_mode == "HDR":
            row = layout.row(align=True)
            row.prop(sceneProperties, "tlm_format")

class TLM_PT_Selection(bpy.types.Panel):
    bl_label = "Selection"
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

            if sceneProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroup":

                if scene.TLM_AtlasList_index >= 0 and len(scene.TLM_AtlasList) > 0:
                    row = layout.row()
                    item = scene.TLM_AtlasList[scene.TLM_AtlasList_index]
                    row.prop_search(sceneProperties, "tlm_atlas_pointer", scene, "TLM_AtlasList", text='Atlas Group')
                else:
                    row = layout.label(text="Add Atlas Groups from the scene lightmapping settings.")

            else:

                row.prop(sceneProperties, "tlm_mesh_lightmap_resolution")
                row = layout.row()
                row.prop(sceneProperties, "tlm_mesh_unwrap_margin")

        row = layout.row(align=True)
        row.operator("tlm.remove_uv_selection")
        row = layout.row(align=True)

class TLM_PT_Additional(bpy.types.Panel):
    bl_label = "Additional"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "TLM_PT_Panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sceneProperties = scene.TLM_SceneProperties