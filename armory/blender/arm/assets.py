import shutil
import os
import stat
import bpy
import arm.utils
from arm import log

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

assets = []
reserved_names = ['return.']
khafile_params = []
khafile_defs = []
khafile_defs_last = []
embedded_data = []
shaders = []
shaders_last = []
shaders_external = []
shader_datas = []
shader_passes = []
shader_passes_assets = {}
shader_cons = {}
# Shader data collected during the export, written by flush_shader_data().
# Item format: filepath -> data
pending_shader_data = {}

def flush_shader_data():
    """Writes out the shader data collected during the export.

    A material is built once per scene that uses it, and because all of
    those builds target the same file, only the last result is kept.
    Writing on each build would give the file a new modification time
    even when its final content is unchanged, which makes Khamake and
    the Haxe compilation server redo work that is already done.
    """
    for filepath, data in pending_shader_data.items():
        arm.utils.write_arm(filepath, data)
    pending_shader_data.clear()

def reset():
    global assets
    global khafile_params
    global khafile_defs
    global khafile_defs_last
    global embedded_data
    global shaders
    global shaders_last
    global shaders_external
    global shader_datas
    global shader_passes
    global shader_cons
    assets = []
    khafile_params = []
    khafile_defs_last = khafile_defs
    khafile_defs = []
    embedded_data = []
    shaders_last = shaders
    shaders = []
    shaders_external = []
    shader_datas = []
    shader_passes = []
    pending_shader_data.clear()
    shader_cons = {}
    shader_cons['mesh_vert'] = []
    shader_cons['depth_vert'] = []
    shader_cons['depth_frag'] = []
    shader_cons['voxel_vert'] = []
    shader_cons['voxel_frag'] = []
    shader_cons['voxel_geom'] = []

def reset_shader_cons():
    # Reset shader comparison arrays to prevent cross-scene shader merging
    global shader_cons
    shader_cons['mesh_vert'] = []
    shader_cons['depth_vert'] = []
    shader_cons['depth_frag'] = []
    shader_cons['voxel_vert'] = []
    shader_cons['voxel_frag'] = []
    shader_cons['voxel_geom'] = []

def add(asset_file):
    global assets

    # Asset already exists, do nothing
    if asset_file in assets:
        return

    asset_file_base = os.path.basename(asset_file)
    for f in assets:
        f_file_base = os.path.basename(f)
        if f_file_base == asset_file_base:
            return

    assets.append(asset_file)

    # Reserved file name
    for f in reserved_names:
        if f in asset_file:
            log.warn(f'File "{asset_file}" contains reserved keyword, this will break C++ builds!')

def add_khafile_def(d):
    global khafile_defs
    if d not in khafile_defs:
        khafile_defs.append(d)

def add_khafile_param(p):
    global khafile_params
    if p not in khafile_params:
        khafile_params.append(p)

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

def add_shader_pass(data_name):
    global shader_passes
    # Shader data for passes are written into single shader_datas.arm file
    add_shader_data(arm.utils.get_fp_build() + '/compiled/Shaders/shader_datas.arm')
    if data_name not in shader_passes:
        shader_passes.append(data_name)

def add_shader_external(file):
    global shaders_external
    shaders_external.append(file)
    name = file.split('/')[-1].split('\\')[-1]
    add_shader(arm.utils.get_fp_build() + '/compiled/Shaders/' + name)

invalidate_enabled = True # Disable invalidating during build process

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def invalidate_shader_compilation() -> None:
    """Marks the generated shaders as needing to be compiled again.

    Called during the build when compiled.inc turned out to have changed.
    The shaders `#include` that file, but Khamake's shader compiler only
    compares a shader against its own output, so it can't see that a
    define changed. Touching the sources makes it notice.

    This used to be done by deleting the compiled shaders and every
    platform's resource directory the moment one of ~127 properties was
    edited, which also threw away the export cache and could run in the
    middle of a build.
    """
    shaders_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Shaders')
    if not os.path.isdir(shaders_path):
        return

    for name in os.listdir(shaders_path):
        if name.endswith('.glsl'):
            try:
                os.utime(os.path.join(shaders_path, name), None)
            except OSError:
                pass

def invalidate_unpacked_data(self, context):
    fp = arm.utils.get_fp_build()
    if os.path.isdir(fp + '/compiled/Assets/unpacked'):
        shutil.rmtree(fp + '/compiled/Assets/unpacked', onerror=remove_readonly)

def invalidate_mesh_cache(self, context):
    if context.object is None or context.object.data is None:
        return
    context.object.data.arm_cached = False

def invalidate_instance_cache(self, context):
    if context.object is None or context.object.data is None:
        return
    invalidate_mesh_cache(self, context)
    for slot in context.object.material_slots:
        slot.material.arm_cached = False

def invalidate_compiler_cache(self, context):
    bpy.data.worlds['Arm'].arm_recompile = True

def shader_equal(sh, ar, shtype):
    # Merge equal shaders
    for e in ar:
        if sh.is_equal(e):
            sh.context.data[shtype] = e.context.data[shtype]
            sh.is_linked = True
            return
    ar.append(sh)

def vs_equal(c, ar):
    shader_equal(c.vert, ar, 'vertex_shader')

def fs_equal(c, ar):
    shader_equal(c.frag, ar, 'fragment_shader')

def gs_equal(c, ar):
    shader_equal(c.geom, ar, 'geometry_shader')

def tcs_equal(c, ar):
    shader_equal(c.tesc, ar, 'tesscontrol_shader')

def tes_equal(c, ar):
    shader_equal(c.tese, ar, 'tesseval_shader')
