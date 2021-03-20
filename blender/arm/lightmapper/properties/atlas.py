import bpy
from bpy.props import *

class TLM_PostAtlasListItem(bpy.types.PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object, description="The object to bake")
    tlm_atlas_lightmap_resolution : EnumProperty(
            items = [('32', '32', 'TODO'),
                    ('64', '64', 'TODO'),
                    ('128', '128', 'TODO'),
                    ('256', '256', 'TODO'),
                    ('512', '512', 'TODO'),
                    ('1024', '1024', 'TODO'),
                    ('2048', '2048', 'TODO'),
                    ('4096', '4096', 'TODO'),
                    ('8192', '8192', 'TODO')],
                    name = "Atlas Lightmap Resolution", 
                    description="TODO",
                    default='256')

    tlm_atlas_repack_on_cleanup : BoolProperty(
        name="Repack on cleanup", 
        description="Postpacking adjusts the UV's. Toggle to resize back to full scale on cleanup.", 
        default=True)

    tlm_atlas_dilation : BoolProperty(
        name="Dilation", 
        description="Adds a blurred background layer that acts as a dilation map.", 
        default=False)

    tlm_atlas_unwrap_margin : FloatProperty(
        name="Unwrap Margin", 
        default=0.1, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR')

    unwrap_modes = [('Lightmap', 'Lightmap', 'Use Blender Lightmap Pack algorithm'),
                 ('SmartProject', 'Smart Project', 'Use Blender Smart Project algorithm')]

    if "blender_xatlas" in bpy.context.preferences.addons.keys():
        unwrap_modes.append(('Xatlas', 'Xatlas', 'Use Xatlas addon packing algorithm'))

    tlm_postatlas_lightmap_unwrap_mode : EnumProperty(
        items = unwrap_modes,
                name = "Unwrap Mode", 
                description="Atlas unwrapping method", 
                default='SmartProject')

class TLM_UL_PostAtlasList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            #In list object counter
            amount = 0

            for obj in bpy.context.scene.objects:
                if obj.TLM_ObjectProperties.tlm_mesh_lightmap_use:
                    if obj.TLM_ObjectProperties.tlm_postpack_object:
                        if obj.TLM_ObjectProperties.tlm_postatlas_pointer == item.name:
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

class TLM_AtlasListItem(bpy.types.PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object, description="The object to bake")
    tlm_atlas_lightmap_resolution : EnumProperty(
        items = [('32', '32', 'TODO'),
                 ('64', '64', 'TODO'),
                 ('128', '128', 'TODO'),
                 ('256', '256', 'TODO'),
                 ('512', '512', 'TODO'),
                 ('1024', '1024', 'TODO'),
                 ('2048', '2048', 'TODO'),
                 ('4096', '4096', 'TODO'),
                 ('8192', '8192', 'TODO')],
                name = "Atlas Lightmap Resolution", 
                description="TODO",
                default='256')

    tlm_atlas_unwrap_margin : FloatProperty(
        name="Unwrap Margin", 
        default=0.1, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR')

    unwrap_modes = [('Lightmap', 'Lightmap', 'Use Blender Lightmap Pack algorithm'),
                 ('SmartProject', 'Smart Project', 'Use Blender Smart Project algorithm'),
                 ('Copy', 'Copy existing', 'Use the existing UV channel')]

    if "blender_xatlas" in bpy.context.preferences.addons.keys():
        unwrap_modes.append(('Xatlas', 'Xatlas', 'Use Xatlas addon packing algorithm'))

    tlm_atlas_lightmap_unwrap_mode : EnumProperty(
        items = unwrap_modes,
                name = "Unwrap Mode", 
                description="Atlas unwrapping method", 
                default='SmartProject')

class TLM_UL_AtlasList(bpy.types.UIList):
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