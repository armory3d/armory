import armutils
import shutil
import os
import bpy

assets = []
khafile_defs = []
khafile_defs_last = []
embedded_data = []
shaders = []
shaders_last = []
shader_datas = []

def reset():
    global assets
    global khafile_defs
    global khafile_defs_last
    global embedded_data
    global shaders
    global shaders_last
    global shader_datas
    assets = []
    khafile_defs_last = khafile_defs
    khafile_defs = []
    embedded_data = []
    shaders_last = shaders
    shaders = []
    shader_datas = []

def add(file):
    global assets
    if file not in assets:
        assets.append(file)

def add_khafile_def(d):
    global khafile_defs
    global khafile_defs_last
    if d not in khafile_defs:
        khafile_defs.append(d)

        wrd = bpy.data.worlds['Arm']
        if not wrd.arm_recompile_trigger and d not in khafile_defs_last:
            wrd.arm_recompile_trigger = True

def add_embedded_data(file):
    global embedded_data
    if file not in embedded_data:
        embedded_data.append(file)

def add_shader(file):
    global shaders
    global shaders_last
    if file not in shaders:
        shaders.append(file)

        wrd = bpy.data.worlds['Arm']
        if not wrd.arm_recompile_trigger and file not in shaders_last:
            wrd.arm_recompile_trigger = True

def add_shader_data(file):
    global shader_datas
    if file not in shader_datas:
        shader_datas.append(file)

def add_shader2(dir_name, data_name):
    add_shader_data('build/compiled/Shaders/' + dir_name + '/' + data_name + '.arm')
    full_name = 'build/compiled/Shaders/' + dir_name + '/' + data_name
    add_shader(full_name + '.vert.glsl')
    add_shader(full_name + '.frag.glsl')

invalidate_enabled = True # Disable invalidating during build process

def invalidate_shader_cache(self, context):
    # compiled.glsl changed, recompile all shaders next time
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Shaders'):
        shutil.rmtree(fp + '/build/compiled/Shaders')
    if os.path.isdir(fp + '/build/compiled/ShaderRaws'):
        shutil.rmtree(fp + '/build/compiled/ShaderRaws')

def invalidate_compiled_data(self, context):
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets'):
        shutil.rmtree(fp + '/build/compiled/Assets')
    if os.path.isdir(fp + '/build/compiled/Shaders'):
        shutil.rmtree(fp + '/build/compiled/Shaders')

def invalidate_mesh_data(self, context):
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets/meshes'):
        shutil.rmtree(fp + '/build/compiled/Assets/meshes')

def invalidate_envmap_data(self, context):
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets/envmaps'):
        shutil.rmtree(fp + '/build/compiled/Assets/envmaps')
