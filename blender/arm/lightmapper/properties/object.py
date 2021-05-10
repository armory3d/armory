import bpy
from bpy.props import *

class TLM_ObjectProperties(bpy.types.PropertyGroup):

    addon_keys = bpy.context.preferences.addons.keys()

    tlm_atlas_pointer : StringProperty(
            name = "Atlas Group",
            description = "",
            default = "")

    tlm_postatlas_pointer : StringProperty(
            name = "Atlas Group",
            description = "Atlas Lightmap Group",
            default = "")

    tlm_uvchannel_pointer : StringProperty(
            name = "UV Channel",
            description = "Select UV Channel to bake to",
            default = "")

    tlm_uvchannel_pointer : BoolProperty(
        name="Enable Lightmapping", 
        description="TODO", 
        default=False)

    tlm_mesh_lightmap_use : BoolProperty(
        name="Enable Lightmapping", 
        description="TODO", 
        default=False)

    tlm_material_ignore : BoolProperty(
        name="Skip material", 
        description="Ignore material for lightmapped object", 
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

    unwrap_modes = [('Lightmap', 'Lightmap', 'TODO'),
                ('SmartProject', 'Smart Project', 'TODO'),
                ('AtlasGroupA', 'Atlas Group (Prepack)', 'Attaches the object to a prepack Atlas group. Will overwrite UV map on build.')]

    tlm_postpack_object : BoolProperty( #CHECK INSTEAD OF ATLASGROUPB
        name="Postpack object", 
        description="Postpack object into an AtlasGroup", 
        default=False)

    if "blender_xatlas" in addon_keys:
        unwrap_modes.append(('Xatlas', 'Xatlas', 'TODO'))

    tlm_mesh_lightmap_unwrap_mode : EnumProperty(
        items = unwrap_modes,
                name = "Unwrap Mode",
                description="TODO", 
                default='SmartProject')

    tlm_mesh_unwrap_margin : FloatProperty(
        name="Unwrap Margin", 
        default=0.1, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR')

    tlm_mesh_filter_override : BoolProperty(
        name="Override filtering", 
        description="Override the scene specific filtering", 
        default=False)

    #FILTERING SETTINGS GROUP
    tlm_mesh_filtering_engine : EnumProperty(
        items = [('OpenCV', 'OpenCV', 'Make use of OpenCV based image filtering (Requires it to be installed first in the preferences panel)'),
                ('Numpy', 'Numpy', 'Make use of Numpy based image filtering (Integrated)')],
                name = "Filtering library", 
                description="Select which filtering library to use.", 
                default='Numpy')

    #Numpy Filtering options
    tlm_mesh_numpy_filtering_mode : EnumProperty(
        items = [('Blur', 'Blur', 'Basic blur filtering.')],
                name = "Filter", 
                description="TODO", 
                default='Blur')

    #OpenCV Filtering options
    tlm_mesh_filtering_mode : EnumProperty(
        items = [('Box', 'Box', 'Basic box blur'),
                    ('Gaussian', 'Gaussian', 'Gaussian blurring'),
                    ('Bilateral', 'Bilateral', 'Edge-aware filtering'),
                    ('Median', 'Median', 'Median blur')],
                name = "Filter", 
                description="TODO", 
                default='Median')

    tlm_mesh_filtering_gaussian_strength : IntProperty(
        name="Gaussian Strength", 
        default=3, 
        min=1, 
        max=50)

    tlm_mesh_filtering_iterations : IntProperty(
        name="Filter Iterations", 
        default=5, 
        min=1, 
        max=50)

    tlm_mesh_filtering_box_strength : IntProperty(
        name="Box Strength", 
        default=1, 
        min=1, 
        max=50)

    tlm_mesh_filtering_bilateral_diameter : IntProperty(
        name="Pixel diameter", 
        default=3, 
        min=1, 
        max=50)

    tlm_mesh_filtering_bilateral_color_deviation : IntProperty(
        name="Color deviation", 
        default=75, 
        min=1, 
        max=100)

    tlm_mesh_filtering_bilateral_coordinate_deviation : IntProperty(
        name="Color deviation", 
        default=75, 
        min=1, 
        max=100)

    tlm_mesh_filtering_median_kernel : IntProperty(
        name="Median kernel", 
        default=3, 
        min=1, 
        max=5)

    tlm_use_default_channel : BoolProperty(
        name="Use default UV channel", 
        description="Will either use or create the default UV Channel 'UVMap_Lightmap' upon build.", 
        default=True)

    tlm_uv_channel : StringProperty(
            name = "UV Channel",
            description = "Use any custom UV Channel for the lightmap",
            default = "UVMap")