import os
import bpy
import subprocess
import arm.utils
import arm.assets as assets
import arm.material.mat_utils as mat_utils
import arm.material.mat_state as mat_state
from arm.material.shader import ShaderData
import arm.material.cycles as cycles
import arm.material.make_mesh as make_mesh
import arm.material.make_transluc as make_transluc
import arm.material.make_overlay as make_overlay
import arm.material.make_depth as make_depth
import arm.material.make_decal as make_decal
import arm.material.make_voxel as make_voxel
import arm.api
import arm.exporter

rpass_hook = None

def build(material, mat_users, mat_armusers):
    mat_state.mat_users = mat_users
    mat_state.mat_armusers = mat_armusers
    mat_state.material = material
    mat_state.nodes = material.node_tree.nodes
    mat_state.data = ShaderData(material)
    mat_state.output_node = cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if mat_state.output_node == None:
        # Place empty material output to keep compiler happy..
        mat_state.output_node = mat_state.nodes.new('ShaderNodeOutputMaterial')

    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    rpasses = mat_utils.get_rpasses(material)
    is_emissive = mat_utils.is_emmisive(material)
    if is_emissive and '_Emission' not in wrd.world_defs:
        wrd.world_defs += '_Emission'
    matname = arm.utils.safesrc(arm.utils.asset_name(material))
    rel_path = arm.utils.build_dir() + '/compiled/Shaders/'
    full_path = arm.utils.get_fp() + '/' + rel_path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    global_elems = []
    if mat_users != None and material in mat_users:
        for bo in mat_users[material]:
            # GPU Skinning
            if arm.utils.export_bone_data(bo):
                global_elems.append({'name': 'bone', 'data': 'short4norm'})
                global_elems.append({'name': 'weight', 'data': 'short4norm'})
            # Instancing
            if bo.arm_instanced != 'Off' or material.arm_particle_flag:
                global_elems.append({'name': 'ipos', 'data': 'float3'})
                if bo.arm_instanced == 'Loc + Rot' or bo.arm_instanced == 'Loc + Rot + Scale':
                    global_elems.append({'name': 'irot', 'data': 'float3'})
                if bo.arm_instanced == 'Loc + Scale' or bo.arm_instanced == 'Loc + Rot + Scale':
                    global_elems.append({'name': 'iscl', 'data': 'float3'})
                
    mat_state.data.global_elems = global_elems

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

        if rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['make_rpass'] != None:
            con = arm.api.drivers[rpdat.rp_driver]['make_rpass'](rp)

        if con != None:
            pass
            
        elif rp == 'mesh':
            con = make_mesh.make(rp, rpasses)

        elif rp == 'shadowmap':
            con = make_depth.make(rp, rpasses, shadowmap=True)

        elif rp == 'translucent':
            con = make_transluc.make(rp)

        elif rp == 'overlay':
            con = make_overlay.make(rp)

        elif rp == 'decal':
            con = make_decal.make(rp)

        elif rp == 'depth':
            con = make_depth.make(rp, rpasses)

        elif rp == 'voxel':
            con = make_voxel.make(rp)

        elif rpass_hook != None:
            con = rpass_hook(rp)

        write_shaders(rel_path, con, rp, matname)

    shader_data_name = matname + '_data'

    if wrd.arm_single_data_file:
        if not 'shader_datas' in arm.exporter.current_output:
            arm.exporter.current_output['shader_datas'] = []
        arm.exporter.current_output['shader_datas'].append(mat_state.data.get()['shader_datas'][0])
    else:
        arm.utils.write_arm(full_path + '/' + matname + '_data.arm', mat_state.data.get())
        shader_data_path = arm.utils.get_fp_build() + '/compiled/Shaders/' + shader_data_name + '.arm'
        assets.add_shader_data(shader_data_path)

    return rpasses, mat_state.data, shader_data_name, bind_constants, bind_textures

def write_shaders(rel_path, con, rpass, matname):
    keep_cache = mat_state.material.arm_cached
    write_shader(rel_path, con.vert, 'vert', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.frag, 'frag', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.geom, 'geom', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.tesc, 'tesc', rpass, matname, keep_cache=keep_cache)
    write_shader(rel_path, con.tese, 'tese', rpass, matname, keep_cache=keep_cache)

def write_shader(rel_path, shader, ext, rpass, matname, keep_cache=True):
    if shader == None or shader.is_linked:
        return

    # TODO: blend context
    if mat_state.material.arm_blending and rpass == 'mesh':
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
