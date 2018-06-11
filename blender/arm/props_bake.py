import arm.utils
import arm.assets
import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *

class ArmBakeListItem(bpy.types.PropertyGroup):
    object_name = bpy.props.StringProperty(
           name="Name",
           description="A name for this item",
           default="")

    res_x = IntProperty(name="X", description="Texture resolution", default=1024)
    res_y = IntProperty(name="Y", description="Texture resolution", default=1024)

class ArmBakeList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "object_name", text="", emboss=False, icon=custom_icon)
            col = row.column()
            col.alignment = 'RIGHT'
            col.label(str(item.res_x) + 'x' + str(item.res_y))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon=custom_icon)

class ArmBakeListNewItem(bpy.types.Operator):
    # Add a new item to the list
    bl_idname = "arm_bakelist.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        scn = context.scene
        scn.arm_bakelist.add()
        scn.arm_bakelist_index = len(scn.arm_bakelist) - 1
        return{'FINISHED'}


class ArmBakeListDeleteItem(bpy.types.Operator):
    # Delete the selected item from the list
    bl_idname = "arm_bakelist.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        scn = context.scene
        return len(scn.arm_bakelist) > 0

    def execute(self, context):
        scn = context.scene
        list = scn.arm_bakelist
        index = scn.arm_bakelist_index

        list.remove(index)

        if index > 0:
            index = index - 1

        scn.arm_bakelist_index = index
        return{'FINISHED'}

class ArmBakeButton(bpy.types.Operator):
    '''Bake textures for listed objects'''
    bl_idname = 'arm.bake_textures'
    bl_label = 'Bake'

    def execute(self, context):
        scn = context.scene
        if len(scn.arm_bakelist) == 0:
            return{'FINISHED'}

        self.report({'INFO'}, "Once baked, hit 'Armory Bake - Apply' to pack lightmaps")

        # At least one material required for now..
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            if len(ob.material_slots) == 0:
                if not 'MaterialDefault' in bpy.data.materials:
                    mat = bpy.data.materials.new(name='MaterialDefault')
                    mat.use_nodes = True
                else:
                    mat = bpy.data.materials['MaterialDefault']
                ob.data.materials.append(mat)

        # Single user materials
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            for slot in ob.material_slots:
                # Temp material already exists
                if slot.material.name.endswith('_temp'):
                    continue
                n = slot.material.name + '_' + ob.name + '_temp'
                if not n in bpy.data.materials:
                    slot.material = slot.material.copy()
                    slot.material.name = n

        # Images for baking
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            img_name = ob.name + '_baked'
            sc = scn.arm_bakelist_scale / 100
            rx = o.res_x * sc
            ry = o.res_y * sc
            # Get image
            if img_name not in bpy.data.images or bpy.data.images[img_name].size[0] != rx or bpy.data.images[img_name].size[1] != ry:
                img = bpy.data.images.new(img_name, rx, ry)
                img.name = img_name # Force img_name (in case Blender picked img_name.001)
            else:
                img = bpy.data.images[img_name]
            for slot in ob.material_slots:
                # Add image nodes
                mat = slot.material
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                if 'Baked Image' in nodes:
                    img_node = nodes['Baked Image']
                else:
                    img_node = nodes.new('ShaderNodeTexImage')
                    img_node.name = 'Baked Image'
                    img_node.location = (100, 100)
                    img_node.image = img
                img_node.select = True
                nodes.active = img_node
        
        if bpy.app.version >= (2, 80, 1):
            obs = bpy.context.view_layer.objects
        else:
            obs = bpy.context.scene.objects

        # Unwrap
        active = obs.active
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            if bpy.app.version >= (2, 80, 1):
                uv_layers = ob.data.uv_layers
            else:
                uv_layers = ob.data.uv_textures
            if not 'UVMap_baked' in uv_layers:
                uvmap = uv_layers.new(name='UVMap_baked')
                uv_layers.active_index = len(uv_layers) - 1
                obs.active = ob
                if scn.arm_bakelist_unwrap == 'Lightmap Pack':
                    bpy.ops.uv.lightmap_pack('EXEC_SCREEN', PREF_CONTEXT='ALL_FACES')
                else:
                    bpy.ops.object.select_all(action='DESELECT')
                    if bpy.app.version >= (2, 80, 1):
                        ob.select_set(action='SELECT')
                    else:
                        ob.select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.uv.smart_project('EXEC_SCREEN')
            else:
                for i in range(0, len(uv_layers)):
                    if uv_layers[i].name == 'UVMap_baked':
                        uv_layers.active_index = i
                        break
        obs.active = active

        # Materials for runtime
        # TODO: use single mat per object
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            img_name = ob.name + '_baked'
            for slot in ob.material_slots:
                n = slot.material.name[:-5] + '_baked'
                if not n in bpy.data.materials:
                    mat = bpy.data.materials.new(name=n)
                    mat.use_nodes = True
                    mat.use_fake_user = True
                    nodes = mat.node_tree.nodes
                    img_node = nodes.new('ShaderNodeTexImage')
                    img_node.name = 'Baked Image'
                    img_node.location = (100, 100)
                    img_node.image = bpy.data.images[img_name]
                    if bpy.app.version >= (2, 80, 1):
                        mat.node_tree.links.new(img_node.outputs[0], nodes['Principled BSDF'].inputs[0])
                    else:
                        mat.node_tree.links.new(img_node.outputs[0], nodes['Diffuse BSDF'].inputs[0])
                else:
                    mat = bpy.data.materials[n]
                    nodes = mat.node_tree.nodes
                    nodes['Baked Image'].image = bpy.data.images[img_name]

        # Bake
        bpy.ops.object.select_all(action='DESELECT')
        for o in scn.arm_bakelist:
            if bpy.app.version >= (2, 80, 1):
                scn.objects[o.object_name].select_set(action='SELECT')
            else:
                scn.objects[o.object_name].select = True
        obs.active = scn.objects[scn.arm_bakelist[0].object_name]
        bpy.ops.object.bake('INVOKE_DEFAULT', type='COMBINED')
        bpy.ops.object.select_all(action='DESELECT')

        return{'FINISHED'}

class ArmBakeApplyButton(bpy.types.Operator):
    '''Pack baked textures and restore materials'''
    bl_idname = 'arm.bake_apply'
    bl_label = 'Apply'

    def execute(self, context):
        scn = context.scene
        if len(scn.arm_bakelist) == 0:
            return{'FINISHED'}
        # Remove leftover _baked materials for removed objects
        for mat in bpy.data.materials:
            if mat.name.endswith('_baked'):
                has_user = False
                for ob in bpy.data.objects:
                    if ob.type == 'MESH' and mat.name.endswith('_' + ob.name + '_baked'):
                        has_user = True
                        break
                if not has_user:
                    bpy.data.materials.remove(mat, True)
        # Recache lightmaps
        arm.assets.invalidate_unpacked_data(None, None)
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            img_name = ob.name + '_baked'
            # Save images
            bpy.data.images[img_name].pack(as_png=True)
            bpy.data.images[img_name].save()
            for slot in ob.material_slots:
                mat = slot.material
                # Remove temp material
                if mat.name.endswith('_temp'):
                    old = slot.material
                    slot.material = bpy.data.materials[old.name.split('_' + ob.name)[0]]
                    bpy.data.materials.remove(old, True)
        # Restore uv slots
        for o in scn.arm_bakelist:
            ob = scn.objects[o.object_name]
            if bpy.app.version >= (2, 80, 1):
                uv_layers = ob.data.uv_layers
            else:
                uv_layers = ob.data.uv_textures
            uv_layers.active_index = 0

        return{'FINISHED'}

class ArmBakeSpecialsMenu(bpy.types.Menu):
    bl_label = "Bake"
    bl_idname = "arm_bakelist_specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.bake_add_all")
        layout.operator("arm.bake_add_selected")
        layout.operator("arm.bake_clear_all")

class ArmBakeAddAllButton(bpy.types.Operator):
    '''Fill the list with scene objects'''
    bl_idname = 'arm.bake_add_all'
    bl_label = 'Add All'

    def execute(self, context):
        scn = context.scene
        scn.arm_bakelist.clear()
        for ob in scn.objects:
            if ob.type == 'MESH':
                scn.arm_bakelist.add().object_name = ob.name
        return{'FINISHED'}

class ArmBakeAddSelectedButton(bpy.types.Operator):
    '''Add selected objects to the list'''
    bl_idname = 'arm.bake_add_selected'
    bl_label = 'Add Selected'

    def contains(self, scn, ob):
        for o in scn.arm_bakelist:
            if o.object_name == ob.name:
                return True
        return False

    def execute(self, context):
        scn = context.scene
        for ob in context.selected_objects:
            if ob.type == 'MESH' and not self.contains(scn, ob):
                scn.arm_bakelist.add().object_name = ob.name
        return{'FINISHED'}

class ArmBakeClearAllButton(bpy.types.Operator):
    '''Clear the list'''
    bl_idname = 'arm.bake_clear_all'
    bl_label = 'Clear'

    def execute(self, context):
        scn = context.scene
        scn.arm_bakelist.clear()
        return{'FINISHED'}

def register():
    bpy.utils.register_class(ArmBakeListItem)
    bpy.utils.register_class(ArmBakeList)
    bpy.utils.register_class(ArmBakeListNewItem)
    bpy.utils.register_class(ArmBakeListDeleteItem)
    bpy.utils.register_class(ArmBakeButton)
    bpy.utils.register_class(ArmBakeApplyButton)
    bpy.utils.register_class(ArmBakeSpecialsMenu)
    bpy.utils.register_class(ArmBakeAddAllButton)
    bpy.utils.register_class(ArmBakeAddSelectedButton)
    bpy.utils.register_class(ArmBakeClearAllButton)
    bpy.types.Scene.arm_bakelist_scale = FloatProperty(name="Resolution", description="Resolution scale", default=100.0, min=1, max=1000, soft_min=1, soft_max=100.0, subtype='PERCENTAGE')
    bpy.types.Scene.arm_bakelist = bpy.props.CollectionProperty(type=ArmBakeListItem)
    bpy.types.Scene.arm_bakelist_index = bpy.props.IntProperty(name="Index for my_list", default=0)
    bpy.types.Scene.arm_bakelist_unwrap = EnumProperty(
        items = [('Lightmap Pack', 'Lightmap Pack', 'Lightmap Pack'),
                 ('Smart UV Project', 'Smart UV Project', 'Smart UV Project')],
        name = "UV Unwrap", default='Smart UV Project')

def unregister():
    bpy.utils.unregister_class(ArmBakeListItem)
    bpy.utils.unregister_class(ArmBakeList)
    bpy.utils.unregister_class(ArmBakeListNewItem)
    bpy.utils.unregister_class(ArmBakeListDeleteItem)
    bpy.utils.unregister_class(ArmBakeButton)
    bpy.utils.unregister_class(ArmBakeApplyButton)
    bpy.utils.unregister_class(ArmBakeSpecialsMenu)
    bpy.utils.unregister_class(ArmBakeAddAllButton)
    bpy.utils.unregister_class(ArmBakeAddSelectedButton)
    bpy.utils.unregister_class(ArmBakeClearAllButton)
