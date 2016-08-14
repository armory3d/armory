import math
import os
import bpy
from bpy.props import *

def material_update(self, context):
    scene = context.scene
    if scene.material_prop != '':
        
        for i in range(0, 5):
            update_texture_index(context, i)

        # Set brush textures
        scene.brushindex1_prop = -1
        scene.brushindex2_prop = -1
        scene.brushindex3_prop = -1
        scene.brushindex4_prop = -1
        scene.brushindex5_prop = -1

        imageindices = [
            scene.imageindex1_prop,
            scene.imageindex2_prop,
            scene.imageindex3_prop,
            scene.imageindex4_prop,
            scene.imageindex5_prop]

        i = 0
        for ii in imageindices:
            if ii != -1:
                brush_name = 'brush_' + str(i + 1)
                texture = bpy.data.textures[brush_name]
                texture.image = bpy.data.images[ii]
                j = 0
                for brush in bpy.data.textures:
                    if brush.name == brush_name:
                        if i == 0:
                            scene.brushindex1_prop = j
                        elif i == 1:
                            scene.brushindex2_prop = j
                        elif i == 2:
                            scene.brushindex3_prop = j
                        elif i == 3:
                            scene.brushindex4_prop = j
                        elif i == 4:
                            scene.brushindex5_prop = j
                        break
                    j += 1
            i += 1


def find_node_by_link(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link.from_node


def get_image_name(node_group, node, inp_index):
    if node.inputs[inp_index].is_linked:
        image_node = find_node_by_link(
            node_group, node, node.inputs[inp_index])
        if image_node.type == 'TEX_IMAGE':
            return image_node.image.name


def update_texture_index(context, input_index):
    scene = context.scene

    mat = bpy.data.materials[scene.material_prop]
    for n in mat.node_tree.nodes:
        if n.type == 'GROUP' and n.node_tree.name.split('.', 1)[0] == 'Armory PBR':
            node = n
            break
    image_name = get_image_name(mat.node_tree, node, input_index)

    i = 0
    image_index = -1
    for image in bpy.data.images:
        if image_name == image.name:
            image_index = i
            break
        i += 1
    if image_index == -1:
        return

    # Get PBR material node
    obj = context.image_paint_object
    mat = obj.active_material
    for n in mat.node_tree.nodes:
        if n.type == 'GROUP' and n.node_tree.name == 'Armory PBR':
            node = n
            break
    image_name = get_image_name(mat.node_tree, node, input_index)

    # Save image index to correct slot
    i = 0
    for slot in mat.texture_paint_images:
        slot_name = slot.name
        if slot_name == image_name:
            if i == 0:
                scene.imageindex1_prop = image_index
            elif i == 1:
                scene.imageindex2_prop = image_index
            elif i == 2:
                scene.imageindex3_prop = image_index
            elif i == 3:
                scene.imageindex4_prop = image_index
            elif i == 4:
                scene.imageindex5_prop = image_index
            break
        i += 1

def get_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {
                            'window': window,
                            'screen': screen,
                            'area': area,
                            'region': region}
                        return override


def brushtoggle_update(self, context):
    if context.scene['PPBrush'] == 1:
        material_update(self, context)
        override = get_override()
        bpy.ops.pp.brush_operator(override, 'INVOKE_DEFAULT')


def init_scene_properties():
    bpy.types.Scene.PPBrush = BoolProperty(
        name="PBR Brush", description="Enable multi-texture painting",
        update=brushtoggle_update)

    bpy.types.Scene.material_prop = bpy.props.StringProperty(
        name="Material", description="PBR Material",
        update=material_update, default="")

    bpy.types.Scene.imageindex1_prop = bpy.props.IntProperty(
        name="Texture Index 1", description="Texture index",
        default=-1)

    bpy.types.Scene.imageindex2_prop = bpy.props.IntProperty(
        name="Texture Index 2", description="Texture index",
        default=-1)

    bpy.types.Scene.imageindex3_prop = bpy.props.IntProperty(
        name="Texture Index 3", description="Texture index",
        default=-1)

    bpy.types.Scene.imageindex4_prop = bpy.props.IntProperty(
        name="Texture Index 4", description="Texture index",
        default=-1)

    bpy.types.Scene.imageindex5_prop = bpy.props.IntProperty(
        name="Texture Index 5", description="Texture index",
        default=-1)

    bpy.types.Scene.brushindex1_prop = bpy.props.IntProperty(
        name="Brush Index 1", description="Brush index",
        default=-1)

    bpy.types.Scene.brushindex2_prop = bpy.props.IntProperty(
        name="Brush Index 2", description="Brush index",
        default=-1)

    bpy.types.Scene.brushindex3_prop = bpy.props.IntProperty(
        name="Brush Index 3", description="Brush index",
        default=-1)

    bpy.types.Scene.brushindex4_prop = bpy.props.IntProperty(
        name="Brush Index 4", description="Brush index",
        default=-1)

    bpy.types.Scene.brushindex5_prop = bpy.props.IntProperty(
        name="Brush Index 5", description="Brush index",
        default=-1)

    bpy.types.Scene.PPTextureWidth = IntProperty(
        name="Width", description="Texture Width",
        default=1024)

    bpy.types.Scene.PPTextureHeight = IntProperty(
        name="Height", description="Texture Height",
        default=1024)


def paint_strokes(strokes):
    bpy.ops.paint.image_paint(stroke=strokes)


def paint(mouse_path):
    ts = bpy.context.tool_settings
    bradius = ts.unified_paint_settings.size * 2
    bstrength = ts.image_paint.brush.strength
    strokes = []
    i = 0
    for x, y in mouse_path:
        strokes.append({
            'name': '',
            'location': (0, 0, 0),
            'mouse': (x, y),
            'size': bradius,
            'pen_flip': False,
            'is_start': False,
            'pressure': bstrength,
            'time': i})
        i += 1

    scene = bpy.context.scene
    obj = bpy.context.image_paint_object
    slot = obj.active_material.paint_active_slot
    brush = bpy.context.tool_settings.image_paint.brush

    i = scene.brushindex1_prop
    if i != -1:
        brush.texture = bpy.data.textures[i]
        obj.active_material.paint_active_slot = 0
        paint_strokes(strokes)

    i = scene.brushindex2_prop
    if i != -1:
        brush.texture = bpy.data.textures[i]
        obj.active_material.paint_active_slot = 1
        paint_strokes(strokes)

    i = scene.brushindex3_prop
    if i != -1:
        brush.texture = bpy.data.textures[i]
        obj.active_material.paint_active_slot = 2
        paint_strokes(strokes)

    i = scene.brushindex4_prop
    if i != -1:
        brush.texture = bpy.data.textures[i]
        obj.active_material.paint_active_slot = 3
        paint_strokes(strokes)

    i = scene.brushindex5_prop
    if i != -1:
        brush.texture = bpy.data.textures[i]
        obj.active_material.paint_active_slot = 4
        paint_strokes(strokes)

    obj.active_material.paint_active_slot = slot


class ModalPPBrushOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "pp.brush_operator"
    bl_label = "PBR Brush"
    bl_options = {"INTERNAL"}

    def modal(self, context, event):
        if bpy.context.image_paint_object is None:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if self.mouse_down:
                # Make points more dense if necessary
                if len(self.last_mouse_path) > 0:
                    lx = self.last_mouse_path[-1][0]
                    ly = self.last_mouse_path[-1][1]
                    dx = event.mouse_region_x - lx
                    dy = event.mouse_region_y - ly
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 16:
                        stepx = (dx / dist) * 16
                        stepy = (dy / dist) * 16
                        for i in range(1, int(dist / 16)):
                            self.mouse_path.append(
                                (int(lx + stepx * i), int(ly + stepy * i)))
                self.mouse_path.append(
                    (event.mouse_region_x, event.mouse_region_y))
                paint(self.mouse_path)
                self.last_mouse_path = self.mouse_path
                self.mouse_path = []
                return {'RUNNING_MODAL'}
            elif context.scene['PPBrush'] == 0:
                return {'FINISHED'}

        elif event.type == 'LEFTMOUSE':
            mx = event.mouse_region_x
            my = event.mouse_region_y
            prefs = bpy.context.user_preferences
            use_region_overlap = prefs.system.use_region_overlap
            view_area = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    view_area = True
                    r = area.regions[4]
                    if use_region_overlap:
                        tools_r = area.regions[1]
                        if mx < tools_r.width + 30 or my < 0 or mx > (r.width - tools_r.width - 30) or my > r.height:
                            return {'PASS_THROUGH'}
                    else: # mx is negative when in tools panel
                        if mx < 30 or my < 0 or mx > r.width - 30 or my > r.height:
                            return {'PASS_THROUGH'}
            if view_area is False:
                return {'PASS_THROUGH'}
            brush = bpy.context.tool_settings.image_paint.brush
            if brush.image_tool != 'DRAW':
                return {'PASS_THROUGH'}
            if context.scene.material_prop == '':
                return {'PASS_THROUGH'}

            if event.value == 'PRESS':
                self.mouse_path.append(
                    (event.mouse_region_x, event.mouse_region_y))
                paint(self.mouse_path)
                self.last_mouse_path = self.mouse_path
                self.mouse_path = []
                self.mouse_down = True
                args = (self, context)
                # Disable undo
                prefs = bpy.context.user_preferences
                self.use_global_undo = prefs.edit.use_global_undo
                self.undo_steps = prefs.edit.undo_steps
                prefs.edit.undo_steps = 0
                prefs.edit.use_global_undo = False
            elif event.value == 'RELEASE':
                # Clear
                self.last_mouse_path = []
                self.mouse_path = []
                self.mouse_down = False
                # Restore undo
                prefs = bpy.context.user_preferences
                prefs.edit.undo_steps = self.undo_steps
                prefs.edit.use_global_undo = self.use_global_undo
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.last_mouse_path = []
            self.mouse_path = []
            self.mouse_down = False
            self.use_global_undo = 0
            self.undo_steps = 0
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


def get_override_smart_project(obj):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {
                        'window': bpy.context.window,
                        'scene': bpy.context.scene,
                        'screen': bpy.context.screen,
                        'blend_data': bpy.context.blend_data,
                        'active_object': bpy.context.active_object,
                        'selected_editable_objects':
                            bpy.context.selected_editable_objects,
                        'area': area,
                        'region': region,
                        'edit_object': obj}
                    return override


class PPSetupButton(bpy.types.Operator):
    bl_idname = "pp.setup"
    bl_label = "Setup"

    def execute(self, context):
        # Switch to cycles
        for scene in bpy.data.scenes:
            scene.render.engine = 'CYCLES'

        # Create textures
        w = context.scene.PPTextureWidth
        h = context.scene.PPTextureHeight
        obj = context.image_paint_object
        basecolor_image = bpy.data.images.new(
            obj.name + "_basecolor", width=w, height=h)
        basecolor_image.pack(as_png=True)
        occlusion_image = bpy.data.images.new(
            obj.name + "_occlusion", width=w, height=h)
        occlusion_image.pack(as_png=True)
        roughness_image = bpy.data.images.new(
            obj.name + "_roughness", width=w, height=h)
        roughness_image.pack(as_png=True)
        metalness_image = bpy.data.images.new(
            obj.name + "_metalness", width=w, height=h)
        metalness_image.pack(as_png=True)
        normal_image = bpy.data.images.new(
            obj.name + "_normal", width=w, height=h)
        normal_image.pack(as_png=True)

        # Unwrap if needed
        if len(obj.data.uv_layers) == 0:
            override = get_override_smart_project(obj)
            bpy.ops.uv.smart_project(override)

        # Import pbr nodes
        import_node_groups()

        # Create material if needed
        if obj.name+'_pbr' not in bpy.data.materials:
            mat = bpy.data.materials.new(name=obj.name+'_pbr')
            mat.use_nodes = True
        else:
            mat = bpy.data.materials[obj.name+'_pbr']

        if len(obj.data.materials) > 0:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        # Setup material
        mat = obj.active_material
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for n in nodes:
            nodes.remove(n)

        out_node = nodes.new('ShaderNodeOutputMaterial')
        out_node.location = 0, 0

        group_node = nodes.new("ShaderNodeGroup")
        group_node.location = -250, 0
        group_node.node_tree = bpy.data.node_groups['Armory PBR']
        links.new(group_node.outputs[0], out_node.inputs[0])
        links.new(group_node.outputs[1], out_node.inputs[2])

        # Connect textures
        basecolor_node = nodes.new('ShaderNodeTexImage')
        basecolor_node.location = -1300, 0
        basecolor_node.image = basecolor_image
        links.new(basecolor_node.outputs[0], group_node.inputs[0])

        occlusion_node = nodes.new('ShaderNodeTexImage')
        occlusion_node.location = -1100, -200
        occlusion_node.image = occlusion_image
        links.new(occlusion_node.outputs[0], group_node.inputs[1])

        roughness_node = nodes.new('ShaderNodeTexImage')
        roughness_node.location = -900, -400
        roughness_node.image = roughness_image
        roughness_node.color_space = 'NONE'
        links.new(roughness_node.outputs[0], group_node.inputs[2])

        metalness_node = nodes.new('ShaderNodeTexImage')
        metalness_node.location = -700, -600
        metalness_node.image = metalness_image
        metalness_node.color_space = 'NONE'
        links.new(metalness_node.outputs[0], group_node.inputs[3])

        normal_node = nodes.new('ShaderNodeTexImage')
        normal_node.location = -500, -800
        normal_node.image = normal_image
        links.new(normal_node.outputs[0], group_node.inputs[4])

        # Create brush texture
        for i in range(1, 6):
            brush = bpy.data.textures.new('brush_' + str(i), 'IMAGE')
            brush.use_fake_user = True

        return{'FINISHED'}


def import_node_groups():
    if bpy.data.node_groups.get('Armory PBR') is None:
            data_path = \
            os.path.dirname(os.path.abspath(__file__)) + '/data.blend'

            with bpy.data.libraries.load(data_path, link=False) as \
            (data_from, data_to):
                data_to.node_groups = ['Armory PBR']


class PPImportNodeGroupsButton(bpy.types.Operator):
    bl_idname = "pp.import_node_groups"
    bl_label = "Import Node Groups"

    def execute(self, context):
        import_node_groups()
        return{'FINISHED'}


class PPSetEnvironmentButton(bpy.types.Operator):
    bl_idname = "pp.set_environment"
    bl_label = "Set Environment"

    def execute(self, context):
        world = bpy.context.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        for n in nodes:
            nodes.remove(n)

        out_node = nodes.new('ShaderNodeOutputWorld')
        out_node.location = 0, 0

        background_node = nodes.new('ShaderNodeBackground')
        background_node.location = -250, 0
        links.new(background_node.outputs[0], out_node.inputs[0])

        sky_node = nodes.new('ShaderNodeTexSky')
        sky_node.location = -500, 0
        sky_node.sky_type = 'PREETHAM'
        sky_node.turbidity = 3.0
        links.new(sky_node.outputs[0], background_node.inputs[0])
        return{'FINISHED'}


class PPExportTexturesButton(bpy.types.Operator):
    bl_idname = "pp.export_textures"
    bl_label = "Export Textures"

    def execute(self, context):
        return{'FINISHED'}


class PPExportSketchFabButton(bpy.types.Operator):
    bl_idname = "pp.export_webgl"
    bl_label = "Export to SketchFab"

    def execute(self, context):
        return{'FINISHED'}


class VIEW3D_PT_tools_imagepaint_pbr(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "imagepaint"
    bl_label = "PBR Painter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label('Textures')
        row = layout.row()
        row.prop(scene, 'PPTextureWidth')
        row.prop(scene, 'PPTextureHeight')
        layout.operator("pp.setup")

        layout.prop(scene, 'PPBrush')
        if 'PPBrush' in scene and scene['PPBrush']:
            layout.prop_search(
                scene, "material_prop", bpy.data,
                "materials", "Material")

        layout.label('Utils')
        box = layout.box()
        box.operator("pp.import_node_groups")
        box.operator("pp.set_environment")

        #layout.label('Export')
        #layout.operator("pp.export_textures")

def register():
    bpy.utils.register_module(__name__)
    init_scene_properties()


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
