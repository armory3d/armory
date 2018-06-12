# Armory 3D Engine
# https://github.com/armory3d/armory
bl_info = {
    "name": "Armory",
    "category": "Render",
    "location": "Properties -> Render -> Armory",
    "description": "3D Game Engine for Blender",
    "author": "Armory3D.org",
    "version": (14, 0, 0),
    "blender": (2, 79, 0),
    "wiki_url": "http://armory3d.org/manual",
    "tracker_url": "https://github.com/armory3d/armory/issues"
}

import os
import sys
import stat
import shutil
import webbrowser
import subprocess
import bpy
import platform
from bpy.types import Operator, AddonPreferences
from bpy.props import *
from bpy.app.handlers import persistent

def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'

class ArmoryAddonPreferences(AddonPreferences):
    bl_idname = __name__

    def sdk_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.sdk_path = bpy.path.reduce_dirs([bpy.path.abspath(self.sdk_path)])[0] + '/'

    def ffmpeg_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.ffmpeg_path = bpy.path.reduce_dirs([bpy.path.abspath(self.ffmpeg_path)])[0]

    def renderdoc_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.renderdoc_path = bpy.path.reduce_dirs([bpy.path.abspath(self.renderdoc_path)])[0]

    sdk_bundled = BoolProperty(name="Bundled SDK", default=True)
    sdk_path = StringProperty(name="SDK Path", subtype="FILE_PATH", update=sdk_path_update, default="")
    show_advanced = BoolProperty(name="Show Advanced", default=False)
    player_gapi_win = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('direct3d11', 'Direct3D11', 'direct3d11')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    player_gapi_linux = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    player_gapi_mac = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    code_editor = EnumProperty(
        items = [('kodestudio', 'Kode Studio', 'kodestudio'),
                 ('default', 'System Default', 'default')],
        name="Code Editor", default='kodestudio', description='Use this editor for editing scripts')
    ui_scale = FloatProperty(name='UI Scale', description='Adjust UI scale for Armory tools', default=1.0, min=1.0, max=4.0)
    renderdoc_path = StringProperty(name="RenderDoc Path", description="Binary path", subtype="FILE_PATH", update=renderdoc_path_update, default="")
    ffmpeg_path = StringProperty(name="FFMPEG Path", description="Binary path", subtype="FILE_PATH", update=ffmpeg_path_update, default="")
    save_on_build = BoolProperty(name="Save on Build", description="Save .blend", default=False)
    legacy_shaders = BoolProperty(name="Legacy Shaders", description="Attempt to compile shaders runnable on older hardware", default=False)
    viewport_controls = EnumProperty(
        items=[('qwerty', 'qwerty', 'qwerty'),
               ('azerty', 'azerty', 'azerty')],
        name="Viewport Controls", default='qwerty', description='Viewport camera mode controls')
    skip_update = BoolProperty(name="", default=False)

    def draw(self, context):
        self.skip_update = False
        layout = self.layout
        layout.label(text="Welcome to Armory! Click 'Save User Settings' at the bottom to keep Armory enabled.")
        p = bundled_sdk_path()
        if os.path.exists(p):
            layout.prop(self, "sdk_bundled")
            if not self.sdk_bundled:
                layout.prop(self, "sdk_path")
        else:
            layout.prop(self, "sdk_path")
        box = layout.box().column()
        box.label("Armory Updater")
        box.label("Note: Development version may run unstable!")
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm_addon.install_git", icon="URL")
        row.operator("arm_addon.update", icon="FILE_REFRESH")
        row.operator("arm_addon.restore")
        box.label("Please restart Blender after successful SDK update.")
        layout.prop(self, "show_advanced")
        if self.show_advanced:
            box = layout.box().column()
            box.prop(self, "player_gapi_" + get_os())
            box.prop(self, "code_editor")
            # box.prop(self, "kha_version")
            box.prop(self, "renderdoc_path")
            box.prop(self, "ffmpeg_path")
            box.prop(self, "viewport_controls")
            box.prop(self, "ui_scale")
            box.prop(self, "save_on_build")
            box.prop(self, "legacy_shaders")

def bundled_sdk_path():
    if get_os() == 'mac':
        # SDK on MacOS is located in .app folder due to security
        p = bpy.app.binary_path
        if p.endswith('Contents/MacOS/blender'):
            return p[:-len('Contents/MacOS/blender')] + '/armsdk/'
        else:
            return p[:-len('Contents/MacOS/./blender')] + '/armsdk/'
    elif get_os() == 'linux':
        # /blender
        return bpy.app.binary_path.rsplit('/', 1)[0] + '/armsdk/'
    else:
        # /blender.exe
        return bpy.app.binary_path.replace('\\', '/').rsplit('/', 1)[0] + '/armsdk/'

def get_sdk_path(context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["armory"].preferences
    p = bundled_sdk_path()
    if os.path.exists(p) and addon_prefs.sdk_bundled:
        return p
    else:
        return addon_prefs.sdk_path

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update_repo(p, n, gitn = ''):
    if gitn == '':
        gitn = n
    if not os.path.exists(p + '/' + n + '_backup'):
        os.rename(p + '/' + n, p + '/' + n + '_backup')
    if os.path.exists(p + '/' + n):
        shutil.rmtree(p + '/' + n, onerror=remove_readonly)
    subprocess.Popen(['git', 'clone', 'https://github.com/armory3d/' + gitn, p + '/' + n, '--depth=1'])

def restore_repo(p, n):
    if os.path.exists(p + '/' + n + '_backup'):
        if os.path.exists(p + '/' + n):
            shutil.rmtree(p + '/' + n, onerror=remove_readonly)
        os.rename(p + '/' + n + '_backup', p + '/' + n)

class ArmAddonStartButton(bpy.types.Operator):
    '''Start Armory integration'''
    bl_idname = "arm_addon.start"
    bl_label = "Start"
    running = False
    play_in_viewport = False

    def execute(self, context):
        if bpy.app.version >= (2, 80, 1):
            from bl_ui import properties_render
            # properties_render.RENDER_PT_render.COMPAT_ENGINES.add('ARMORY')
            # properties_render.RENDER_PT_output.COMPAT_ENGINES.add('ARMORY')
            properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_world
            properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add('ARMORY')
            properties_world.WORLD_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            properties_world.EEVEE_WORLD_PT_surface.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_material
            properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add('ARMORY')
            properties_material.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            properties_material.EEVEE_MATERIAL_PT_context_material.COMPAT_ENGINES.add('ARMORY')
            properties_material.EEVEE_MATERIAL_PT_surface.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_object
            properties_object.OBJECT_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_particle
            properties_particle.PARTICLE_MT_specials.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_MT_hair_dynamics_presets.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_context_particles.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_emission.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_hair_dynamics.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_cache.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_velocity.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_rotation.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_physics.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_boidbrain.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_render.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_draw.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_children.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_field_weights.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_force_fields.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_vertexgroups.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_textures.COMPAT_ENGINES.add('ARMORY')
            properties_particle.PARTICLE_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_scene
            properties_scene.SCENE_PT_scene.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_unit.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_color_management.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_audio.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_physics.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_rigid_body_world.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_rigid_body_cache.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_rigid_body_field_weights.COMPAT_ENGINES.add('ARMORY')
            properties_scene.SCENE_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_texture
            properties_texture.TEXTURE_MT_specials.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_context.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_node.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_node_mapping.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_colors.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_clouds.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_wood.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_marble.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_magic.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_blend.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_stucci.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_image_sampling.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_image_mapping.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_musgrave.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_voronoi.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_distortednoise.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TextureSlotPanel.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_mapping.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_influence.COMPAT_ENGINES.add('ARMORY')
            properties_texture.TEXTURE_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_armature
            properties_data_armature.DATA_PT_custom_props_arm.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_bone
            properties_data_bone.BONE_PT_custom_props.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_camera
            properties_data_camera.CAMERA_MT_presets.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.SAFE_AREAS_MT_presets.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_context_camera.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_lens.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_camera_stereoscopy.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_camera_dof.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_camera_background_image.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_camera_display.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_camera_safe_areas.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_custom_props_camera.COMPAT_ENGINES.add('ARMORY')
            properties_data_camera.DATA_PT_custom_props_camera.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_curve
            properties_data_curve.DATA_PT_curve_texture_space.COMPAT_ENGINES.add('ARMORY')
            properties_data_curve.DATA_PT_custom_props_curve.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_lamp
            properties_data_lamp.LAMP_MT_sunsky_presets.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_preview.COMPAT_ENGINES.add('ARMORY')
            # properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_EEVEE_lamp.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_EEVEE_shadow.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_area.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_spot.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_falloff_curve.COMPAT_ENGINES.add('ARMORY')
            properties_data_lamp.DATA_PT_custom_props_lamp.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_lattice
            properties_data_lattice.DATA_PT_custom_props_lattice.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_lightprobe
            properties_data_lightprobe.DATA_PT_context_lightprobe.COMPAT_ENGINES.add('ARMORY')
            properties_data_lightprobe.DATA_PT_lightprobe.COMPAT_ENGINES.add('ARMORY')
            properties_data_lightprobe.DATA_PT_lightprobe_parallax.COMPAT_ENGINES.add('ARMORY')
            properties_data_lightprobe.DATA_PT_lightprobe_display.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_mesh
            properties_data_mesh.MESH_MT_vertex_group_specials.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.MESH_MT_shape_key_specials.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_context_mesh.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_normals.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_texture_space.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_vertex_groups.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_face_maps.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_shape_keys.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_uv_texture.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_vertex_colors.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_customdata.COMPAT_ENGINES.add('ARMORY')
            properties_data_mesh.DATA_PT_custom_props_mesh.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_metaball
            properties_data_metaball.DATA_PT_mball_texture_space.COMPAT_ENGINES.add('ARMORY')
            properties_data_metaball.DATA_PT_custom_props_metaball.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_data_speaker
            properties_data_speaker.DATA_PT_context_speaker.COMPAT_ENGINES.add('ARMORY')
            properties_data_speaker.DATA_PT_speaker.COMPAT_ENGINES.add('ARMORY')
            properties_data_speaker.DATA_PT_distance.COMPAT_ENGINES.add('ARMORY')
            properties_data_speaker.DATA_PT_cone.COMPAT_ENGINES.add('ARMORY')
            properties_data_speaker.DATA_PT_custom_props_speaker.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_physics_cloth
            properties_physics_cloth.PHYSICS_PT_cloth.COMPAT_ENGINES.add('ARMORY')
            properties_physics_cloth.PHYSICS_PT_cloth_cache.COMPAT_ENGINES.add('ARMORY')
            properties_physics_cloth.PHYSICS_PT_cloth_collision.COMPAT_ENGINES.add('ARMORY')
            properties_physics_cloth.PHYSICS_PT_cloth_stiffness.COMPAT_ENGINES.add('ARMORY')
            properties_physics_cloth.PHYSICS_PT_cloth_sewing.COMPAT_ENGINES.add('ARMORY')
            properties_physics_cloth.PHYSICS_PT_cloth_field_weights.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_physics_common
            properties_physics_common.PHYSICS_PT_add.COMPAT_ENGINES.add('ARMORY')
            properties_physics_common.PHYSICS_PT_add.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_physics_softbody
            properties_physics_softbody.PHYSICS_PT_softbody.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_cache.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_goal.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_edge.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_collision.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_solver.COMPAT_ENGINES.add('ARMORY')
            properties_physics_softbody.PHYSICS_PT_softbody_field_weights.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_physics_rigidbody
            properties_physics_rigidbody.PHYSICS_PT_rigid_body.COMPAT_ENGINES.add('ARMORY')
            properties_physics_rigidbody.PHYSICS_PT_rigid_body_collisions.COMPAT_ENGINES.add('ARMORY')
            properties_physics_rigidbody.PHYSICS_PT_rigid_body_dynamics.COMPAT_ENGINES.add('ARMORY')
            properties_physics_rigidbody.PHYSICS_PT_rigid_body_dynamics.COMPAT_ENGINES.add('ARMORY')
            from bl_ui import properties_physics_rigidbody_constraint
            properties_physics_rigidbody_constraint.PHYSICS_PT_rigid_body_constraint.COMPAT_ENGINES.add('ARMORY')

        sdk_path = get_sdk_path(context)
        if sdk_path == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}

        scripts_path = sdk_path + "/armory/blender/"
        sys.path.append(scripts_path)
        import start
        start.register()
        ArmAddonStartButton.running = True

        if not hasattr(bpy.app.handlers, 'scene_update_post'):
            bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)

        return {"FINISHED"}

class ArmAddonStopButton(bpy.types.Operator):
    '''Stop Armory integration'''
    bl_idname = "arm_addon.stop"
    bl_label = "Stop"
 
    def execute(self, context):
        import start
        start.unregister()
        ArmAddonStartButton.running = False
        return {"FINISHED"}

class ArmAddonUpdateButton(bpy.types.Operator):
    '''Update Armory SDK'''
    bl_idname = "arm_addon.update"
    bl_label = "Update SDK"
    bl_description = "Update to the latest development version"
 
    def execute(self, context):
        p = get_sdk_path(context)
        if p == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}
        self.report({'INFO'}, 'Updating, check console for details. Please restart Blender after successful SDK update.')
        print('Armory (add-on v' + str(bl_info['version']) + '): Cloning [armory, iron, haxebullet, haxerecast, zui] repositories')
        os.chdir(p)
        update_repo(p, 'armory')
        update_repo(p, 'iron')
        update_repo(p, 'lib/haxebullet', 'haxebullet')
        update_repo(p, 'lib/haxerecast', 'haxerecast')
        update_repo(p, 'lib/zui', 'zui')
        update_repo(p, 'lib/armory_tools', 'armory_tools')
        update_repo(p, 'lib/iron_format', 'iron_format')
        return {"FINISHED"}

class ArmAddonRestoreButton(bpy.types.Operator):
    '''Update Armory SDK'''
    bl_idname = "arm_addon.restore"
    bl_label = "Restore SDK"
    bl_description = "Restore stable version"
 
    def execute(self, context):
        p = get_sdk_path(context)
        if p == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}
        os.chdir(p)
        restore_repo(p, 'armory')
        restore_repo(p, 'iron')
        restore_repo(p, 'lib/haxebullet')
        restore_repo(p, 'lib/haxerecast')
        restore_repo(p, 'lib/zui')
        restore_repo(p, 'lib/armory_tools')
        restore_repo(p, 'lib/iron_format')
        self.report({'INFO'}, 'Restored stable version')
        return {"FINISHED"}

class ArmAddonInstallGitButton(bpy.types.Operator):
    '''Install Git'''
    bl_idname = "arm_addon.install_git"
    bl_label = "Install Git"
    bl_description = "Git is required for Armory Updater to work"
 
    def execute(self, context):
        webbrowser.open('https://git-scm.com')
        return {"FINISHED"}

@persistent
def on_scene_update_post(scene):
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.ops.arm_addon.start()

def draw_view3d_header(self, context):
    layout = self.layout
    layout.operator("arm_addon.start")

def register():
    bpy.utils.register_module(__name__)
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    else:
        bpy.types.VIEW3D_HT_header.append(draw_view3d_header)

def unregister():
    bpy.ops.arm_addon.stop()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
