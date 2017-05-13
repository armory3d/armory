import bpy
import arm.assets
import arm.utils
import arm.make_state
import arm.log
import arm.material.make_texture
import arm.material.mat_state as mat_state

def get_rp_renderer():
    return bpy.data.cameras[0].rp_renderer

def get_arm_export_tangents():
    return bpy.data.worlds['Arm'].arm_export_tangents

def safesrc(name):
    return arm.utils.safesrc(name)

def get_sdk_path():
    return arm.utils.get_sdk_path()

def tess_enabled():
    return arm.utils.tess_enabled(arm.make_state.target)

def warn(text):
    arm.log.warn(text)

def assets_add(path):
    arm.assets.add(path)

def assets_add_embedded_data(path):
    arm.assets.add_embedded_data(path)

def make_texture(node, name):
    return arm.material.make_texture.make(node, name)

def mat_name():
    return mat_state.material.name

def mat_batch():
    return mat_state.batch

def mat_add_elem(name, size):
    mat_state.data.add_elem(name, size)

def mat_bind_texture(tex):
    mat_state.bind_textures.append(tex)

def mat_texture_grad():
    return mat_state.texture_grad

def mat_get_material():
    return mat_state.material

def mat_get_material_users():
    return mat_state.mat_users
