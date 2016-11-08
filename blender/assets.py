import armutils
import shutil
import os

assets = []
khafile_defs = []
embedded_data = []
shaders = []
shader_datas = []

def reset():
    global assets
    global khafile_defs
    global embedded_data
    global shaders
    global shader_datas
    assets = []
    khafile_defs = []
    embedded_data = []
    shaders = []
    shader_datas = []

def add(file):
    global assets
    if file not in assets:
        assets.append(file)

def add_khafile_def(d):
    global khafile_defs
    if d not in khafile_defs:
        khafile_defs.append(d)

def add_embedded_data(file):
    global embedded_data
    if file not in embedded_data:
        embedded_data.append(file)

def add_shader(file):
    global shaders
    if file not in shaders:
        shaders.append(file)

def add_shader_data(file):
    global shader_datas
    if file not in shader_datas:
        shader_datas.append(file)

def add_shader2(dir_name, data_name):
    add_shader_data('build/compiled/ShaderDatas/' + dir_name + '/' + data_name + '.arm')
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
    if os.path.isdir(fp + '/build/compiled/ShaderDatas'):
        shutil.rmtree(fp + '/build/compiled/ShaderDatas')

def invalidate_compiled_data(self, context):
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets'):
        shutil.rmtree(fp + '/build/compiled/Assets')
    if os.path.isdir(fp + '/build/compiled/ShaderDatas'):
        shutil.rmtree(fp + '/build/compiled/ShaderDatas')

def invalidate_mesh_data(self, context):
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets/meshes'):
        shutil.rmtree(fp + '/build/compiled/Assets/meshes')

def invalidate_envmap_data(self, context):
    fp = armutils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets/envmaps'):
        shutil.rmtree(fp + '/build/compiled/Assets/envmaps')
