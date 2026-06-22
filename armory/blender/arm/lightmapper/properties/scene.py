import bpy, os
from bpy.props import *
from .. utility import utility

def transfer_load():
    load_folder = bpy.context.scene.TLM_SceneProperties.tlm_load_folder
    lightmap_folder = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.TLM_EngineProperties.tlm_lightmap_savedir)
    print(load_folder)
    print(lightmap_folder)
    #transfer_assets(True, load_folder, lightmap_folder)

class TLM_SceneProperties(bpy.types.PropertyGroup):

    engines = [('Cycles', 'Cycles', 'Use Cycles for lightmapping')]

    #engines.append(('LuxCoreRender', 'LuxCoreRender', 'Use LuxCoreRender for lightmapping'))
    #engines.append(('OctaneRender', 'Octane Render', 'Use Octane Render for lightmapping'))

    tlm_atlas_pointer : StringProperty(
            name = "Atlas Group",
            description = "Atlas Lightmap Group",
            default = "")

    tlm_postatlas_pointer : StringProperty(
            name = "Atlas Group",
            description = "Atlas Lightmap Group",
            default = "")

    tlm_lightmap_engine : EnumProperty(
        items = engines,
                name = "Lightmap Engine", 
                description="Select which lightmap engine to use.", 
                default='Cycles')

    #SETTINGS GROUP
    tlm_setting_clean_option : EnumProperty(
        items = [('Clean', 'Full Clean', 'Clean lightmap directory and revert all materials'),
                ('CleanMarked', 'Clean marked', 'Clean only the objects marked for lightmapping')],
                name = "Clean mode", 
                description="The cleaning mode, either full or partial clean. Be careful that you don't delete lightmaps you don't intend to delete.", 
                default='Clean')

    tlm_setting_keep_cache_files : BoolProperty(
        name="Keep cache files", 
        description="Keep cache files (non-filtered and non-denoised)", 
        default=True)

    tlm_keep_baked_files : BoolProperty(
        name="Keep bake files", 
        description="Keep the baked lightmap files when cleaning", 
        default=False)

    tlm_repartition_on_clean : BoolProperty(
        name="Repartition on clean", 
        description="Repartition material names on clean", 
        default=False)

    tlm_setting_renderer : EnumProperty(
        items = [('CPU', 'CPU', 'Bake using the processor'),
                ('GPU', 'GPU', 'Bake using the graphics card')],
                name = "Device", 
                description="Select whether to use the CPU or the GPU", 
                default="CPU")

    tlm_setting_scale : EnumProperty(
        items = [('8', '1/8', '1/8th of set scale'),
                ('4', '1/4', '1/4th of set scale'),
                ('2', '1/2', 'Half of set scale'),
                ('1', '1/1', 'Full scale')],
                name = "Lightmap Resolution scale", 
                description="Lightmap resolution scaling. Adjust for previewing.", 
                default="1")

    tlm_setting_supersample : EnumProperty(
        items = [('2x', '2x', 'Double the sampling resolution'),
                ('4x', '4x', 'Quadruple the sampling resolution')],
                name = "Lightmap Supersampling", 
                description="Supersamples the baked lightmap. Increases bake time", 
                default="2x")

    tlm_setting_savedir : StringProperty(
        name="Lightmap Directory", 
        description="Your baked lightmaps will be stored here.", 
        default="Lightmaps", 
        subtype="FILE_PATH")

    tlm_setting_exposure_multiplier : FloatProperty(
        name="Exposure Multiplier", 
        default=0,
        description="0 to disable. Multiplies GI value")

    tlm_alert_on_finish : BoolProperty(
        name="Alert on finish", 
        description="Play a sound when the lightmaps are done.", 
        default=False)

    tlm_setting_apply_scale : BoolProperty(
        name="Apply scale", 
        description="Apply the scale before unwrapping.", 
        default=True)

    tlm_play_sound : BoolProperty(
        name="Play sound on finish", 
        description="Play sound on finish", 
        default=False)

    tlm_compile_statistics : BoolProperty(
        name="Compile statistics", 
        description="Compile time statistics in the lightmap folder.", 
        default=True)

    tlm_apply_on_unwrap : BoolProperty(
        name="Apply scale", 
        description="TODO", 
        default=False)
        
    tlm_save_preprocess_lightmaps : BoolProperty(
        name="Save preprocessed lightmaps", 
        description="TODO", 
        default=False)

    #DENOISE SETTINGS GROUP
    tlm_denoise_use : BoolProperty(
        name="Enable denoising", 
        description="Enable denoising for lightmaps", 
        default=False)

    tlm_denoise_engine : EnumProperty(
        items = [('Integrated', 'Integrated', 'Use the Blender native denoiser (Compositor; Slow)'),
                ('OIDN', 'Intel Denoiser', 'Use Intel denoiser (CPU powered)'),
                ('Optix', 'Optix Denoiser', 'Use Nvidia Optix denoiser (GPU powered)')],
                name = "Denoiser", 
                description="Select which denoising engine to use.", 
                default='Integrated')

    #FILTERING SETTINGS GROUP
    tlm_filtering_use : BoolProperty(
        name="Enable denoising", 
        description="Enable denoising for lightmaps", 
        default=False)

    tlm_filtering_engine : EnumProperty(
        items = [('OpenCV', 'OpenCV', 'Make use of OpenCV based image filtering (Requires it to be installed first in the preferences panel)'),
                ('Shader', 'Shader', 'Make use of GPU offscreen shader to filter')],
                name = "Filtering library", 
                description="Select which filtering library to use.", 
                default='OpenCV')

    #Numpy Filtering options
    tlm_numpy_filtering_mode : EnumProperty(
        items = [('Blur', 'Blur', 'Basic blur filtering.')],
                name = "Filter", 
                description="TODO", 
                default='Blur')

    #OpenCV Filtering options
    tlm_filtering_mode : EnumProperty(
        items = [('Box', 'Box', 'Basic box blur'),
                    ('Gaussian', 'Gaussian', 'Gaussian blurring'),
                    ('Bilateral', 'Bilateral', 'Edge-aware filtering'),
                    ('Median', 'Median', 'Median blur')],
                name = "Filter", 
                description="TODO", 
                default='Median')

    tlm_filtering_gaussian_strength : IntProperty(
        name="Gaussian Strength", 
        default=3, 
        min=1, 
        max=50)

    tlm_filtering_iterations : IntProperty(
        name="Filter Iterations", 
        default=5, 
        min=1, 
        max=50)

    tlm_filtering_box_strength : IntProperty(
        name="Box Strength", 
        default=1, 
        min=1, 
        max=50)

    tlm_filtering_bilateral_diameter : IntProperty(
        name="Pixel diameter", 
        default=3, 
        min=1, 
        max=50)

    tlm_filtering_bilateral_color_deviation : IntProperty(
        name="Color deviation", 
        default=75, 
        min=1, 
        max=100)

    tlm_filtering_bilateral_coordinate_deviation : IntProperty(
        name="Coordinate deviation", 
        default=75, 
        min=1, 
        max=100)

    tlm_filtering_median_kernel : IntProperty(
        name="Median kernel", 
        default=3, 
        min=1, 
        max=5)

    tlm_clamp_hdr : BoolProperty(
        name="Enable HDR Clamp", 
        description="Clamp HDR Value", 
        default=False)

    tlm_clamp_hdr_value : IntProperty(
        name="HDR Clamp value", 
        default=10, 
        min=0, 
        max=20)

    #Encoding properties
    tlm_encoding_use : BoolProperty(
        name="Enable encoding", 
        description="Enable encoding for lightmaps", 
        default=False)

    tlm_encoding_device : EnumProperty(
        items = [('CPU', 'CPU', 'Todo'),
                ('GPU', 'GPU', 'Todo.')],
                name = "Encoding Device", 
                description="TODO", 
                default='CPU')

    encoding_modes_1 = [('RGBM', 'RGBM', '8-bit HDR encoding. Good for compatibility, good for memory but has banding issues.'),
                    ('RGBD', 'RGBD', '8-bit HDR encoding. Similar to RGBM.'),
                    ('HDR', 'HDR', '32-bit HDR encoding. Best quality, but high memory usage and not compatible with all devices.'),
                    ('SDR', 'SDR', '8-bit flat encoding.')]

    encoding_modes_2 = [('RGBD', 'RGBD', '8-bit HDR encoding. Similar to RGBM.'),
                    ('LogLuv', 'LogLuv', '8-bit HDR encoding. Different.'),
                    ('HDR', 'HDR', '32-bit HDR encoding. Best quality, but high memory usage and not compatible with all devices.'),
                    ('SDR', 'SDR', '8-bit flat encoding.')]
    
    tlm_encoding_mode_a : EnumProperty(
        items = encoding_modes_1,
                name = "Encoding Mode", 
                description="TODO", 
                default='HDR')

    tlm_encoding_mode_b : EnumProperty(
        items = encoding_modes_2,
                name = "Encoding Mode", 
                description="RGBE 32-bit Radiance HDR File", 
                default='HDR')

    tlm_encoding_range : IntProperty(
        name="Encoding range", 
        description="Higher gives a larger HDR range, but also gives more banding.", 
        default=6, 
        min=1, 
        max=255)

    tlm_decoder_setup : BoolProperty(
        name="Use decoder", 
        description="Apply a node for decoding.", 
        default=False)

    tlm_split_premultiplied : BoolProperty(
        name="Split for premultiplied", 
        description="Some game engines doesn't support non-premultiplied files. This splits the alpha channel to a separate file.", 
        default=False)

    tlm_encoding_colorspace : EnumProperty(
        items = [('XYZ', 'XYZ', 'TODO'),
                ('sRGB', 'sRGB', 'TODO'),
                ('NonColor', 'Non-Color', 'TODO'),
                ('ACES', 'Linear ACES', 'TODO'),
                ('Linear', 'Linear', 'TODO'),
                ('FilmicLog', 'Filmic Log', 'TODO')],
            name = "Color Space", 
            description="TODO", 
            default='Linear')

    tlm_compression : IntProperty(
        name="PNG Compression", 
        description="0 = No compression. 100 = Maximum compression.", 
        default=0, 
        min=0, 
        max=100)
    
    tlm_format : EnumProperty(
        items = [('RGBE', 'HDR', '32-bit RGBE encoded .hdr files. No compression available.'),
                 ('EXR', 'EXR', '32-bit OpenEXR format.')],
                name = "Format", 
                description="Select default 32-bit format", 
                default='RGBE')

    tlm_override_object_settings : BoolProperty(
        name="Override settings", 
        description="TODO", 
        default=False)

    tlm_mesh_lightmap_resolution : EnumProperty(
        items = [('32', '32', 'TODO'),
                 ('64', '64', 'TODO'),
                 ('128', '128', 'TODO'),
                 ('256', '256', 'TODO'),
                 ('512', '512', 'TODO'),
                 ('1024', '1024', 'TODO'),
                 ('2048', '2048', 'TODO'),
                 ('4096', '4096', 'TODO'),
                 ('8192', '8192', 'TODO')],
                name = "Lightmap Resolution", 
                description="TODO", 
                default='256')

    tlm_mesh_lightmap_unwrap_mode : EnumProperty(
        items = [('Lightmap', 'Lightmap', 'TODO'),
                 ('SmartProject', 'Smart Project', 'TODO'),
                 ('AtlasGroupA', 'Atlas Group (Prepack)', 'Attaches the object to a prepack Atlas group. Will overwrite UV map on build.'),
                 ('Xatlas', 'Xatlas', 'TODO')],
                name = "Unwrap Mode", 
                description="TODO", 
                default='SmartProject')

    tlm_postpack_object : BoolProperty( #CHECK INSTEAD OF ATLASGROUPB
        name="Postpack object", 
        description="Postpack object into an AtlasGroup", 
        default=False)

    tlm_mesh_unwrap_margin : FloatProperty(
        name="Unwrap Margin", 
        default=0.1, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR')

    tlm_headless : BoolProperty(
        name="Don't apply materials", 
        description="Headless; Do not apply baked materials on finish.", 
        default=False)

    tlm_atlas_mode : EnumProperty(
        items = [('Prepack', 'Pre-packing', 'Todo.'),
                 ('Postpack', 'Post-packing', 'Todo.')],
                name = "Atlas mode", 
                description="TODO", 
                default='Prepack')

    tlm_alert_sound : EnumProperty(
        items = [('dash', 'Dash', 'Dash alert'),
                ('noot', 'Noot', 'Noot alert'),
                ('gentle', 'Gentle', 'Gentle alert'),
                ('pingping', 'Ping', 'Ping alert')],
                name = "Alert sound", 
                description="Alert sound when lightmap building finished.", 
                default="gentle")

    tlm_metallic_clamp : EnumProperty(
        items = [('ignore', 'Ignore', 'Ignore clamping'),
                ('skip', 'Skip', 'Skip baking metallic materials'),
                ('zero', 'Zero', 'Set zero'),
                ('limit', 'Limit', 'Clamp to 0.9')],
                name = "Metallic clamping", 
                description="TODO.", 
                default="ignore")

    tlm_texture_interpolation : EnumProperty(
        items = [('Smart', 'Smart', 'Bicubic when magnifying.'),
                ('Cubic', 'Cubic', 'Cubic interpolation'),
                ('Closest', 'Closest', 'No interpolation'),
                ('Linear', 'Linear', 'Linear')],
                name = "Texture interpolation", 
                description="Texture interpolation.", 
                default="Linear")

    tlm_texture_extrapolation : EnumProperty(
        items = [('REPEAT', 'Repeat', 'Repeat in both direction.'),
                ('EXTEND', 'Extend', 'Extend by repeating edge pixels.'),
                ('CLIP', 'Clip', 'Clip to image size')],
                name = "Texture extrapolation", 
                description="Texture extrapolation.", 
                default="EXTEND")

    tlm_verbose : BoolProperty(
        name="Verbose", 
        description="Verbose console output", 
        default=False)

    tlm_compile_statistics : BoolProperty(
        name="Compile statistics", 
        description="Compile lightbuild statistics", 
        default=False)

    tlm_override_bg_color : BoolProperty(
        name="Override background", 
        description="Override background color, black by default.", 
        default=False)

    tlm_override_color : FloatVectorProperty(name="Color",
        description="Background color for baked maps", 
        subtype='COLOR', 
        default=[0.5,0.5,0.5])

    tlm_reset_uv : BoolProperty(
        name="Remove Lightmap UV", 
        description="Remove existing UV maps for lightmaps.", 
        default=False)

    tlm_apply_modifiers : BoolProperty(
        name="Apply modifiers", 
        description="Apply all modifiers to objects.", 
        default=True)

    tlm_batch_mode : BoolProperty(
        name="Batch mode", 
        description="Batch collections.", 
        default=False)

    tlm_network_render : BoolProperty(
        name="Enable network rendering", 
        description="Enable network rendering (Unstable).", 
        default=False)

    tlm_network_paths : PointerProperty(
        name="Network file", 
        description="Network instruction file", 
        type=bpy.types.Text)

    tlm_network_dir : StringProperty(
        name="Network directory", 
        description="Use a path that is accessible to all your network render devices.", 
        default="", 
        subtype="FILE_PATH")

    tlm_cmft_path : StringProperty(
        name="CMFT Path", 
        description="The path to the CMFT binaries", 
        default="", 
        subtype="FILE_PATH")
    
    tlm_create_spherical : BoolProperty(
        name="Create spherical texture", 
        description="Merge cubemap to a 360 spherical texture.", 
        default=False)

    tlm_write_sh : BoolProperty(
        name="Calculate SH coefficients", 
        description="Calculates spherical harmonics coefficients to a file.", 
        default=False)

    tlm_write_radiance : BoolProperty(
        name="Write radiance images", 
        description="Writes out the radiance images.", 
        default=False)

    tlm_invert_direction : BoolProperty(
        name="Invert direction", 
        description="Inverts the direction.", 
        default=False)

    tlm_environment_probe_resolution : EnumProperty(
        items = [('32', '32', 'TODO'),
                 ('64', '64', 'TODO'),
                 ('128', '128', 'TODO'),
                 ('256', '256', 'TODO'),
                 ('512', '512', 'TODO'),
                 ('1024', '1024', 'TODO'),
                 ('2048', '2048', 'TODO'),
                 ('4096', '4096', 'TODO'),
                 ('8192', '8192', 'TODO')],
                name = "Probe Resolution", 
                description="TODO", 
                default='256')

    tlm_environment_probe_engine : EnumProperty(
        items = [('BLENDER_EEVEE', 'Eevee', 'TODO'),
                 ('CYCLES', 'Cycles', 'TODO')],
                name = "Probe Render Engine", 
                description="TODO", 
                default='BLENDER_EEVEE')

    tlm_load_folder : StringProperty(
        name="Load Folder",
        description="Load existing lightmaps from folder",
        subtype="DIR_PATH")

    tlm_load_atlas : BoolProperty(
        name="Load lightmaps based on atlas sets", 
        description="Use the current Atlas list.", 
        default=False)

    tlm_utility_set : EnumProperty(
        items = [('Scene', 'Scene', 'Set for all objects in the scene.'),
                 ('Selection', 'Selection', 'Set for selected objects.'),
                 ('Enabled', 'Enabled', 'Set for objects that has been enabled for lightmapping.')],
                name = "Set", 
                description="Utility selection set", 
                default='Scene')

    tlm_resolution_weight : EnumProperty(
        items = [('Single', 'Single', 'Set a single resolution for all objects.'),
                 ('Dimension', 'Dimension', 'Distribute resolutions based on object dimensions.'),
                 ('Surface', 'Surface', 'Distribute resolutions based on mesh surface area.'),
                 ('Volume', 'Volume', 'Distribute resolutions based on mesh volume.')],
                name = "Resolution weight", 
                description="Method for setting resolution value", 
                default='Single')
        #Todo add vertex color option

    tlm_resolution_min : EnumProperty(
        items = [('32', '32', 'TODO'),
                 ('64', '64', 'TODO'),
                 ('128', '128', 'TODO'),
                 ('256', '256', 'TODO'),
                 ('512', '512', 'TODO'),
                 ('1024', '1024', 'TODO'),
                 ('2048', '2048', 'TODO'),
                 ('4096', '4096', 'TODO')],
                name = "Minimum resolution", 
                description="Minimum distributed resolution", 
                default='32')

    tlm_resolution_max : EnumProperty(
        items = [('64', '64', 'TODO'),
                 ('128', '128', 'TODO'),
                 ('256', '256', 'TODO'),
                 ('512', '512', 'TODO'),
                 ('1024', '1024', 'TODO'),
                 ('2048', '2048', 'TODO'),
                 ('4096', '4096', 'TODO')],
                name = "Maximum resolution", 
                description="Maximum distributed resolution", 
                default='256')

    tlm_remove_met_spec_link : BoolProperty(
        name="Remove image link", 
        description="Removes the connected node on metallic or specularity set disable", 
        default=False)

    tlm_utility_context : EnumProperty(
        items = [('SetBatching', 'Set Batching', 'Set batching options. Allows to set lightmap options for multiple objects.'),
                 ('EnvironmentProbes', 'Environment Probes', 'Options for rendering environment probes. Cubemaps and panoramic HDRs for external engines'),
                 ('LoadLightmaps', 'Load Lightmaps', 'Options for loading pre-built lightmaps.'),
                 ('NetworkRender', 'Network Rendering', 'Distribute lightmap building across multiple machines.'),
                 ('MaterialAdjustment', 'Material Adjustment', 'Allows adjustment of multiple materials at once.'),
                 ('TexelDensity', 'Texel Density', 'Allows setting texel densities of the UV.'),
                 ('GLTFUtil', 'GLTF Utilities', 'GLTF related material utilities.')],
                name = "Utility Context", 
                description="Set Utility Context", 
                default='SetBatching')

    tlm_addon_uimode : EnumProperty(
        items = [('Simple', 'Simple', 'TODO'),
                 ('Advanced', 'Advanced', 'TODO')],
                name = "UI Mode", 
                description="TODO", 
                default='Simple')

class TLM_GroupListItem(bpy.types.PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object, description="The object to bake")

class TLM_UL_GroupList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            amount = 0

            for obj in bpy.context.scene.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_mesh_lightmap_unwrap_mode == "AtlasGroupA":
                        if obj.TLM_ObjectProperties.tlm_atlas_pointer == item.name:
                            amount = amount + 1

            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.label(text=item.tlm_atlas_lightmap_resolution)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(text=str(amount))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)