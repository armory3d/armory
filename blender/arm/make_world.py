import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
from typing import List

import arm.write_probes as write_probes
import arm.assets as assets
import arm.utils
import arm.node_utils as node_utils
import arm.log as log
import arm.make_state as state
from arm.material import make_shader, mat_state
from arm.material.shader import ShaderContext, Shader

callback = None

def build():
    worlds = []
    for scene in bpy.data.scenes:
        if scene.arm_export and scene.world is not None and scene.world not in worlds:
            worlds.append(scene.world)
            # create_world_shaders(scene.world)


def create_world_shaders(world: bpy.types.World, out_shader_datas: List):
    """Creates fragment and vertex shaders for the given world."""
    world_name = arm.utils.safestr(world.name)

    shader_props = {
        'name': 'world_' + world_name,
        'depth_write': False,
        'compare_mode': 'less',
        'cull_mode': 'clockwise',
        'color_attachments': ['_HDR'],
        'vertex_elements': [{'name': 'pos', 'data': 'float3'}, {'name': 'nor', 'data': 'float3'}]
    }
    shader_data = {'name': world_name + '_data', 'contexts': [shader_props]}

    # ShaderContext expects a material, but using a world also works
    shader_context = ShaderContext(world, shader_data, shader_props)
    vert = shader_context.make_vert()
    frag = shader_context.make_frag()

    vert.add_out('vec3 normal')
    vert.add_uniform('mat4 SMVP')

    frag.add_include('compiled.inc')
    frag.add_in('vec3 normal')
    frag.add_out('vec4 fragColor')

    vert.write('''normal = nor;
    vec4 position = SMVP * vec4(pos, 1.0);
    gl_Position = vec4(position);''')

    build_node_tree(world, frag, vert)

    frag.write('fragColor = vec4(0.0);')

    # TODO: Rework shader export so that it doesn't depend on materials
    # to prevent workaround code like this
    rel_path = os.path.join(arm.utils.build_dir(), 'compiled', 'Shaders')
    full_path = os.path.join(arm.utils.get_fp(), rel_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    # Output: world_[world_name].[frag/vert].glsl
    make_shader.write_shader(rel_path, shader_context.vert, 'vert', world_name, 'world')
    make_shader.write_shader(rel_path, shader_context.frag, 'frag', world_name, 'world')

    # Write shader data file
    shader_data_file = 'world_' + world_name + '_data.arm'
    arm.utils.write_arm(os.path.join(full_path, shader_data_file), {'shader_datas': shader_context.data})
    shader_data_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Shaders', shader_data_file)
    assets.add_shader_data(shader_data_path)


def build_node_tree(world: bpy.types.World, frag: Shader, vert: Shader):
    """Generates the shader code for the given world."""
    world_name = arm.utils.safestr(world.name)
    world.world_defs = ''
    rpdat = arm.utils.get_rp()

    if callback is not None:
        callback()

    # Traverse world node tree
    is_parsed = False
    if world.node_tree is not None:
        output_node = node_utils.get_node_by_type(world.node_tree, 'OUTPUT_WORLD')
        if output_node is not None:
            parse_world_output(world, output_node)
            is_parsed = True

    if not is_parsed:
        solid_mat = rpdat.arm_material_model == 'Solid'
        if rpdat.arm_irradiance and not solid_mat:
            world.world_defs += '_Irr'
        c = world.color
        world.arm_envtex_color = [c[0], c[1], c[2], 1.0]
        world.arm_envtex_strength = 1.0

    # Clear to color if no texture or sky is provided
    if '_EnvSky' not in world.world_defs and '_EnvTex' not in world.world_defs:
        if '_EnvImg' not in world.world_defs:
            world.world_defs += '_EnvCol'
        # Irradiance json file name
        world.arm_envtex_name = world_name
        world.arm_envtex_irr_name = world_name
        write_probes.write_color_irradiance(world_name, world.arm_envtex_color)

    # film_transparent
    if bpy.context.scene is not None and hasattr(bpy.context.scene.render, 'film_transparent') and bpy.context.scene.render.film_transparent:
        world.world_defs += '_EnvTransp'
        world.world_defs += '_EnvCol'

    # Clouds enabled
    if rpdat.arm_clouds:
        world.world_defs += '_EnvClouds'

    if '_EnvSky' in world.world_defs or '_EnvTex' in world.world_defs or '_EnvImg' in world.world_defs or '_EnvClouds' in world.world_defs:
        world.world_defs += '_EnvStr'

def parse_world_output(world, node):
    if node.inputs[0].is_linked:
        surface_node = node_utils.find_node_by_link(world.node_tree, node, node.inputs[0])
        parse_surface(world, surface_node)

def parse_surface(world, node):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    solid_mat = rpdat.arm_material_model == 'Solid'

    # Extract environment strength
    if node.type == 'BACKGROUND':

        # Append irradiance define
        if rpdat.arm_irradiance and not solid_mat:
            wrd.world_defs += '_Irr'

        world.arm_envtex_color = node.inputs[0].default_value
        world.arm_envtex_strength = node.inputs[1].default_value

        # Strength
        if node.inputs[0].is_linked:
            color_node = node_utils.find_node_by_link(world.node_tree, node, node.inputs[0])
            parse_color(world, color_node)

def parse_color(world, node):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'

    # Env map included
    if node.type == 'TEX_ENVIRONMENT' and node.image is not None:

        image = node.image
        filepath = image.filepath

        if image.packed_file is None and not os.path.isfile(arm.utils.asset_path(filepath)):
            log.warn(world.name + ' - unable to open ' + image.filepath)
            return

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        base = tex_file.rsplit('.', 1)
        ext = base[1].lower()

        if ext == 'hdr':
            target_format = 'HDR'
        else:
            target_format = 'JPEG'
        do_convert = ext != 'hdr' and ext != 'jpg'
        if do_convert:
            if ext == 'exr':
                tex_file = base[0] + '.hdr'
                target_format = 'HDR'
            else:
                tex_file = base[0] + '.jpg'
                target_format = 'JPEG'

        if image.packed_file is not None:
            # Extract packed data
            unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + tex_file
            filepath = unpack_filepath

            if do_convert:
                if not os.path.isfile(unpack_filepath):
                    arm.utils.unpack_image(image, unpack_filepath, file_format=target_format)

            elif not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)

            assets.add(unpack_filepath)
        else:
            if do_convert:
                unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
                if not os.path.exists(unpack_path):
                    os.makedirs(unpack_path)
                converted_path = unpack_path + '/' + tex_file
                filepath = converted_path
                # TODO: delete cache when file changes
                if not os.path.isfile(converted_path):
                    arm.utils.convert_image(image, converted_path, file_format=target_format)
                assets.add(converted_path)
            else:
                # Link image path to assets
                assets.add(arm.utils.asset_path(image.filepath))

        # Generate prefiltered envmaps
        world.arm_envtex_name = tex_file
        world.arm_envtex_irr_name = tex_file.rsplit('.', 1)[0]
        disable_hdr = target_format == 'JPEG'

        mip_count = world.arm_envtex_num_mips
        mip_count = write_probes.write_probes(filepath, disable_hdr, mip_count, arm_radiance=rpdat.arm_radiance)

        world.arm_envtex_num_mips = mip_count

        # Append envtex define
        world.world_defs += '_EnvTex'
        # Append LDR define
        if disable_hdr:
            world.world_defs += '_EnvLDR'
        # Append radiance define
        if rpdat.arm_irradiance and rpdat.arm_radiance and not mobile_mat:
            wrd.world_defs += '_Rad'

    # Static image background
    elif node.type == 'TEX_IMAGE':
        image = node.image
        filepath = image.filepath

        if image.packed_file != None:
            # Extract packed data
            filepath = arm.utils.build_dir() + '/compiled/Assets/unpacked'
            unpack_path = arm.utils.get_fp() + filepath
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(arm.utils.asset_path(image.filepath))

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        world.arm_envtex_name = tex_file

    # Append sky define
    elif node.type == 'TEX_SKY':
        # Match to cycles
        world.arm_envtex_strength *= 0.1

        world.world_defs += '_EnvSky'
        assets.add_khafile_def('arm_hosek')

        world.arm_envtex_sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
        world.arm_envtex_turbidity = node.turbidity
        world.arm_envtex_ground_albedo = node.ground_albedo

        # Irradiance json file name
        wname = arm.utils.safestr(world.name)
        world.arm_envtex_irr_name = wname
        write_probes.write_sky_irradiance(wname)

        # Radiance
        if rpdat.arm_radiance and rpdat.arm_irradiance and not mobile_mat:
            wrd.world_defs += '_Rad'
            hosek_path = 'armory/Assets/hosek/'
            sdk_path = arm.utils.get_sdk_path()
            # Use fake maps for now
            assets.add(sdk_path + '/' + hosek_path + 'hosek_radiance.hdr')
            for i in range(0, 8):
                assets.add(sdk_path + '/' + hosek_path + 'hosek_radiance_' + str(i) + '.hdr')

            world.arm_envtex_name = 'hosek'
            world.arm_envtex_num_mips = 8
