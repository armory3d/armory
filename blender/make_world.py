import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import json
import write_probes
import assets
import utils

def find_node(node_group, to_node, target_socket):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == target_socket:
            return link.from_node

def get_output_node(tree):
    for n in tree.nodes:
        if n.type == 'OUTPUT_WORLD':
            return n

def buildNodeTrees(active_worlds):
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure Assets dir exists
    if not os.path.exists('build/compiled/Assets/materials'):
        os.makedirs('build/compiled/Assets/materials')
    
    # Export world nodes
    world_outputs = []
    for world in active_worlds:
        output = buildNodeTree(world)
        world_outputs.append(output)
    return world_outputs

def buildNodeTree(world):
    output = {}
    dat = {}
    output['material_datas'] = [dat]
    dat['name'] = utils.safe_filename(world.name) + '_material'
    context = {}
    dat['contexts'] = [context]
    context['name'] = 'world'
    context['bind_constants'] = []
    context['bind_textures'] = []
    
    bpy.data.worlds['Arm'].world_defs = ''
    
    # Traverse world node tree
    output_node = get_output_node(world.node_tree)
    if output_node != None:
        parse_world_output(world, output_node, context)
    
    # Clear to color if no texture or sky is provided
    wrd = bpy.data.worlds['Arm']
    if '_EnvSky' not in wrd.world_defs and '_EnvTex' not in wrd.world_defs:
        wrd.world_defs += '_EnvCol'
        # Irradiance json file name
        world.world_envtex_name = world.name
        world.world_envtex_irr_name = world.name
        write_probes.write_color_irradiance(world.name, world.world_envtex_color)

    # Clouds enabled
    if wrd.generate_clouds:
        wrd.world_defs += '_EnvClouds'

    # Shadows disabled
    if wrd.generate_shadows == False:
        wrd.world_defs += '_NoShadows'

    # Percentage closer soft shadows
    if wrd.generate_pcss:
        wrd.world_defs += '_PCSS'
        sdk_path = utils.get_sdk_path()
        assets.add(sdk_path + 'armory/Assets/noise64.png')
        assets.add_embedded_data('noise64.png')

    # Alternative models
    if wrd.diffuse_oren_nayar:
        wrd.world_defs += '_OrenNayar'

    if wrd.voxelgi:
        wrd.world_defs += '_VoxelGI'
        wrd.world_defs += '_Rad' # Always do radiance for voxels

    # Enable probes
    for cam in bpy.data.cameras:
        if cam.is_probe:
            wrd.world_defs += '_Probes'
            break

    # Data will be written after render path has been processed to gather all defines
    return output

def write_output(output):
    # Add datas to khafile
    dir_name = 'world'
    # Append world defs
    wrd = bpy.data.worlds['Arm']
    data_name = 'world' + wrd.world_defs
    
    # Reference correct shader context
    dat = output['material_datas'][0]
    dat['shader'] = data_name + '/' + data_name
    assets.add_shader2(dir_name, data_name)

    # Write material json
    path = 'build/compiled/Assets/materials/'
    asset_path = path + dat['name'] + '.arm'
    utils.write_arm(asset_path, output)
    assets.add(asset_path)

def parse_world_output(world, node, context):
    if node.inputs[0].is_linked:
        surface_node = find_node(world.node_tree, node, node.inputs[0])
        parse_surface(world, surface_node, context)
    
def parse_surface(world, node, context):
    # Extract environment strength
    if node.type == 'BACKGROUND':
        # Strength
        envmap_strength_const = {}
        envmap_strength_const['name'] = 'envmapStrength'
        envmap_strength_const['float'] = node.inputs[1].default_value
        # Always append for now, even though envmapStrength is not always needed
        context['bind_constants'].append(envmap_strength_const)
        
        if node.inputs[0].is_linked:
            color_node = find_node(world.node_tree, node, node.inputs[0])
            parse_color(world, color_node, context, envmap_strength_const)

        # Cache results
        world.world_envtex_color = node.inputs[0].default_value
        world.world_envtex_strength = envmap_strength_const['float']

def parse_color(world, node, context, envmap_strength_const):       
    # Env map included
    if node.type == 'TEX_ENVIRONMENT':
        envmap_strength_const['float'] *= 2.0 # Match to cycles

        texture = {}
        context['bind_textures'].append(texture)
        texture['name'] = 'envmap'
        
        image = node.image
        filepath = image.filepath

        if image.packed_file != None:
            # Extract packed data
            filepath = '/build/compiled/Assets/unpacked'
            unpack_path = utils.get_fp() + filepath
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(utils.safe_assetpath(image.filepath))

        # Reference image name
        texture['file'] = utils.extract_filename(image.filepath)
        texture['file'] = utils.safe_filename(texture['file'])

        # Generate prefiltered envmaps
        generate_radiance = bpy.data.worlds['Arm'].generate_radiance
        world.world_envtex_name = texture['file']
        world.world_envtex_irr_name = texture['file'].rsplit('.', 1)[0]
        disable_hdr = image.filepath.endswith('.jpg')
        mip_count = world.world_envtex_num_mips
        
        mip_count = write_probes.write_probes(filepath, disable_hdr, mip_count, generate_radiance=generate_radiance)
        
        world.world_envtex_num_mips = mip_count
        # Append envtex define
        bpy.data.worlds['Arm'].world_defs += '_EnvTex'
        # Append LDR define
        if disable_hdr:
            bpy.data.worlds['Arm'].world_defs += '_EnvLDR'
        # Append radiance define
        if generate_radiance:
            bpy.data.worlds['Arm'].world_defs += '_Rad'
    
    # Append sky define
    elif node.type == 'TEX_SKY':
        envmap_strength_const['float'] *= 0.25 # Match to Cycles
        
        bpy.data.worlds['Arm'].world_defs += '_EnvSky'
        # Append sky properties to material
        const = {}
        const['name'] = 'sunDirection'
        sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
        sun_direction[1] *= -1 # Fix Y orientation
        const['vec3'] = list(sun_direction)
        context['bind_constants'].append(const)
        
        world.world_envtex_sun_direction = sun_direction
        world.world_envtex_turbidity = node.turbidity
        world.world_envtex_ground_albedo = node.ground_albedo
        
        # Irradiance json file name
        world.world_envtex_irr_name = world.name
        write_probes.write_sky_irradiance(world.name)

        # Radiance
        if bpy.data.worlds['Arm'].generate_radiance_sky and bpy.data.worlds['Arm'].generate_radiance:
            bpy.data.worlds['Arm'].world_defs += '_Rad'
            
            sdk_path = utils.get_sdk_path()
            # Use fake maps for now
            assets.add(sdk_path + 'armory/Assets/hosek/hosek_radiance.hdr')
            for i in range(0, 8):
                assets.add(sdk_path + 'armory/Assets/hosek/hosek_radiance_' + str(i) + '.hdr')
            
            world.world_envtex_name = 'hosek'
            world.world_envtex_num_mips = 8
