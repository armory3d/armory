import shutil
import os
import stat
import bpy
import arm.utils

assets = []
reserved_names = ['return.']
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
        # Reserved file name
        for s in reserved_names:
            if s in file:
                print('Armory Warning: File "{0}" contains reserved keyword, this will break C++ builds!'.format(file))

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
    global shaders_last
    if file not in shaders:
        shaders.append(file)

def add_shader_data(file):
    global shader_datas
    if file not in shader_datas:
        shader_datas.append(file)

def add_shader2(dir_name, data_name):
    add_shader_data(arm.utils.build_dir() + '/compiled/Shaders/' + dir_name + '/' + data_name + '.arm')
    full_name = arm.utils.build_dir() + '/compiled/Shaders/' + dir_name + '/' + data_name
    add_shader(full_name + '.vert.glsl')
    add_shader(full_name + '.frag.glsl')

invalidate_enabled = True # Disable invalidating during build process

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def invalidate_shader_cache(self, context):
    # compiled.glsl changed, recompile all shaders next time
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Shaders'):
        shutil.rmtree(fp + '/compiled/Shaders', onerror=remove_readonly)
    if os.path.isdir(fp + '/compiled/ShaderRaws'):
        shutil.rmtree(fp + '/compiled/ShaderRaws', onerror=remove_readonly)
    if os.path.isdir(fp + '/html5-resources'):
        shutil.rmtree(fp + '/html5-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/krom-resources'):
        shutil.rmtree(fp + '/krom-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/windowed/krom-resources'):
        shutil.rmtree(fp + '/windowed/krom-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/windows-resources'):
        shutil.rmtree(fp + '/windows-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/linux-resources'):
        shutil.rmtree(fp + '/linux-resources', onerror=remove_readonly)
    if os.path.isdir(fp + '/osx-resources'):
        shutil.rmtree(fp + '/osx-resources', onerror=remove_readonly)

def invalidate_compiled_data(self, context):
    global invalidate_enabled
    if invalidate_enabled == False:
        return
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets'):
        shutil.rmtree(fp + '/compiled/Assets', onerror=remove_readonly)
    if os.path.isdir(fp + '/compiled/Shaders'):
        shutil.rmtree(fp + '/compiled/Shaders', onerror=remove_readonly)
    if os.path.isdir(fp + '/compiled/ShaderRaws'):
        shutil.rmtree(fp + '/compiled/ShaderRaws', onerror=remove_readonly)

def invalidate_mesh_data(self, context):
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets/meshes'):
        shutil.rmtree(fp + '/compiled/Assets/meshes', onerror=remove_readonly)

def invalidate_envmap_data(self, context):
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets/envmaps'):
        shutil.rmtree(fp + '/compiled/Assets/envmaps', onerror=remove_readonly)
