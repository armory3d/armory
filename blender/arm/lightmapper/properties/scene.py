import bpy
from bpy.props import *

class TLM_SceneProperties(bpy.types.PropertyGroup):

    engines = [('Cycles', 'Cycles', 'Use Cycles for lightmapping')]

    #engines.append(('LuxCoreRender', 'LuxCoreRender', 'Use LuxCoreRender for lightmapping'))
    #engines.append(('OctaneRender', 'Octane Render', 'Use Octane Render for lightmapping'))

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
        name="Enable filtering", 
        description="Enable filtering for lightmaps", 
        default=False)

    tlm_filtering_engine : EnumProperty(
        items = [('OpenCV', 'OpenCV', 'Make use of OpenCV based image filtering (Requires it to be installed first in the preferences panel)'),
                ('Numpy', 'Numpy', 'Make use of Numpy based image filtering (Integrated)')],
                name = "Filtering library", 
                description="Select which filtering library to use.", 
                default='Numpy')

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
        name="Color deviation", 
        default=75, 
        min=1, 
        max=100)

    tlm_filtering_median_kernel : IntProperty(
        name="Median kernel", 
        default=3, 
        min=1, 
        max=5)

    #Encoding properties
    tlm_encoding_use : BoolProperty(
        name="Enable encoding", 
        description="Enable encoding for lightmaps", 
        default=False)

    tlm_encoding_mode : EnumProperty(
        items = [('RGBM', 'RGBM', '8-bit HDR encoding. Good for compatibility, good for memory but has banding issues.'),
                    ('LogLuv', 'LogLuv', '8-bit HDR encoding. Different.'),
                    ('HDR', 'HDR', '32-bit HDR encoding. Best quality, but high memory usage and not compatible with all devices.')],
                name = "Encoding Mode", 
                description="TODO", 
                default='HDR')

    tlm_encoding_range : IntProperty(
        name="Encoding range", 
        description="Higher gives a larger HDR range, but also gives more banding.", 
        default=6, 
        min=1, 
        max=10)

    tlm_encoding_armory_setup : BoolProperty(
        name="Use Armory decoder", 
        description="TODO", 
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
                 ('CopyExisting', 'Copy Existing', 'TODO'),
                 ('AtlasGroup', 'Atlas Group', 'TODO')],
                name = "Unwrap Mode", 
                description="TODO", 
                default='SmartProject')

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