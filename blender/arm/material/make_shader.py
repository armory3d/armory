import os
import subprocess
from typing import Dict, List, Tuple

import bpy
from bpy.types import Material
from bpy.types import Object

import arm.api
import arm.assets as assets
import arm.exporter
import arm.log as log
import arm.material.cycles as cycles
import arm.material.make_decal as make_decal
import arm.material.make_depth as make_depth
import arm.material.make_mesh as make_mesh
import arm.material.make_overlay as make_overlay
import arm.material.make_transluc as make_transluc
import arm.material.make_voxel as make_voxel
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
from arm.material.shader import Shader, ShaderContext, ShaderData
import arm.utils

if arm.is_reload(__name__):
    arm.api = arm.reload_module(arm.api)
    assets = arm.reload_module(assets)
    arm.exporter = arm.reload_module(arm.exporter)
    log = arm.reload_module(log)
    cycles = arm.reload_module(cycles)
    make_decal = arm.reload_module(make_decal)
    make_depth = arm.reload_module(make_depth)
    make_mesh = arm.reload_module(make_mesh)
    make_overlay = arm.reload_module(make_overlay)
    make_transluc = arm.reload_module(make_transluc)
    make_voxel = arm.reload_module(make_voxel)
    mat_state = arm.reload_module(mat_state)
    mat_utils = arm.reload_module(mat_utils)
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader, ShaderContext, ShaderData
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

rpass_hook = None


def build(material: Material, mat_users: Dict[Material, List[Object]], mat_armusers) -> Tuple:
    mat_state.mat_users = mat_users
    mat_state.mat_armusers = mat_armusers
    mat_state.material = material
    mat_state.nodes = material.node_tree.nodes
    mat_state.data = ShaderData(material)
    mat_state.output_node = cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if mat_state.output_node is None:
        # Place empty material output to keep compiler happy..
        mat_state.output_node = mat_state.nodes.new('ShaderNodeOutputMaterial')

    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    rpasses = mat_utils.get_rpasses(material)
    matname = arm.utils.safesrc(arm.utils.asset_name(material))
    rel_path = arm.utils.build_dir() + '/compiled/Shaders/'
    full_path = arm.utils.get_fp() + '/' + rel_path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    make_instancing_and_skinning(material, mat_users)

    bind_constants = dict()
    bind_textures = dict()

    for rp in rpasses:
        car = []
        bind_constants[rp] = car
        mat_state.bind_constants = car
        tar = []
        bind_textures[rp] = tar
        mat_state.bind_textures = tar

        con = None

        if rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['make_rpass'] is not None:
            con = arm.api.drivers[rpdat.rp_driver]['make_rpass'](rp)

        if con is not None:
            pass

        elif rp == 'mesh':
            con = make_mesh.make(rp, rpasses)

        elif rp == 'shadowmap':
            con = make_depth.make(rp, rpasses, shadowmap=True)

        elif rp == 'translucent':
            con = make_transluc.make(rp)

        elif rp == 'refraction':
            con = make_mesh.make(rp, rpasses)

        elif rp == 'overlay':
            con = make_overlay.make(rp)

        elif rp == 'decal':
            con = make_decal.make(rp)

        elif rp == 'depth':
            con = make_depth.make(rp, rpasses)

        elif rp == 'voxel':
            con = make_voxel.make(rp)

        elif rpass_hook is not None:
            con = rpass_hook(rp)

        write_shaders(rel_path, con, rp, matname)

    shader_data_name = matname + '_data'

    if wrd.arm_single_data_file:
        if 'shader_datas' not in arm.exporter.current_output:
            arm.exporter.current_output['shader_datas'] = []
        arm.exporter.current_output['shader_datas'].append(mat_state.data.get()['shader_datas'][0])
    else:
        arm.utils.write_arm(full_path + '/' + matname + '_data.arm', mat_state.data.get())
        shader_data_path = arm.utils.get_fp_build() + '/compiled/Shaders/' + shader_data_name + '.arm'
        assets.add_shader_data(shader_data_path)

    return rpasses, mat_state.data, shader_data_name, bind_constants, bind_textures


def write_shaders(rel_path: str, con: ShaderContext, rpass: str, matname: str) -> None:
    keep_cache = mat_state.material.arm_cached
    write_shader(rel_path, con.vert, 'vert', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.frag, 'frag', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.geom, 'geom', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.tesc, 'tesc', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.tese, 'tese', rpass, matname, keep_cache=keep_cache)


def write_shader(rel_path: str, shader: Shader, ext: str, rpass: str, matname: str, keep_cache=True) -> None:
    if shader is None or shader.is_linked:
        return

    # TODO: blend context
    if rpass == 'mesh' and mat_state.material.arm_blending:
        rpass = 'blend'

    file_ext = '.glsl'
    if shader.noprocessing:
        # Use hlsl directly
        hlsl_dir = arm.utils.build_dir() + '/compiled/Hlsl/'
        if not os.path.exists(hlsl_dir):
            os.makedirs(hlsl_dir)
        file_ext = '.hlsl'
        rel_path = rel_path.replace('/compiled/Shaders/', '/compiled/Hlsl/')

    shader_file = matname + '_' + rpass + '.' + ext + file_ext
    shader_path = arm.utils.get_fp() + '/' + rel_path + '/' + shader_file
    assets.add_shader(shader_path)
    if not os.path.isfile(shader_path) or not keep_cache:
        with open(shader_path, 'w') as f:
            f.write(shader.get())

        if shader.noprocessing:
            cwd = os.getcwd()
            os.chdir(arm.utils.get_fp() + '/' + rel_path)
            hlslbin_path = arm.utils.get_sdk_path() + '/lib/armory_tools/hlslbin/hlslbin.exe'
            prof = 'vs_5_0' if ext == 'vert' else 'ps_5_0' if ext == 'frag' else 'gs_5_0'
            # noprocessing flag - gets renamed to .d3d11
            args = [hlslbin_path.replace('/', '\\').replace('\\\\', '\\'), shader_file, shader_file[:-4] + 'glsl', prof]
            if ext == 'vert':
                args.append('-i')
                args.append('pos')
            proc = subprocess.call(args)
            os.chdir(cwd)


def make_instancing_and_skinning(mat: Material, mat_users: Dict[Material, List[Object]]) -> None:
    """Build material with instancing or skinning if enabled.
    If the material is a custom material, only validation checks for instancing are performed."""
    global_elems = []
    if mat_users is not None and mat in mat_users:
        # Whether there are both an instanced object and a not instanced object with this material
        instancing_usage = [False, False]
        mat_state.uses_instancing = False

        for bo in mat_users[mat]:
            if mat.arm_custom_material == '':
                # Morph Targets
                if arm.utils.export_morph_targets(bo):
                    global_elems.append({'name': 'morph', 'data': 'short2norm'})
                # GPU Skinning
                if arm.utils.export_bone_data(bo):
                    global_elems.append({'name': 'bone', 'data': 'short4norm'})
                    global_elems.append({'name': 'weight', 'data': 'short4norm'})

            # Instancing
            inst = bo.arm_instanced
            if inst != 'Off' or mat.arm_particle_flag:
                instancing_usage[0] = True
                mat_state.uses_instancing = True

                if mat.arm_custom_material == '':
                    global_elems.append({'name': 'ipos', 'data': 'float3'})
                    if 'Rot' in inst:
                        global_elems.append({'name': 'irot', 'data': 'float3'})
                    if 'Scale' in inst:
                        global_elems.append({'name': 'iscl', 'data': 'float3'})

            elif inst == 'Off':
                # Ignore children of instanced objects, they are instanced even when set to 'Off'
                instancing_usage[1] = bo.parent is None or bo.parent.arm_instanced == 'Off'

        if instancing_usage[0] and instancing_usage[1]:
            # Display a warning for invalid instancing configurations
            # See https://github.com/armory3d/armory/issues/2072
            log.warn(f'Material "{mat.name}" has both instanced and not instanced objects, objects might flicker!')

    if mat.arm_custom_material == '':
        mat_state.data.global_elems = global_elems
