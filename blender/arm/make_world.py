import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import arm.write_probes as write_probes
import arm.assets as assets
import arm.utils
import arm.node_utils as node_utils
import arm.log as log
import arm.make_state as state

callback = None

def build():
    worlds = []
    for scene in bpy.data.scenes:
        if scene.arm_export and scene.world != None and scene.world not in worlds:
            worlds.append(scene.world)
            build_node_tree(scene.world)

def build_node_tree(world):
    wname = arm.utils.safestr(world.name)
    wrd = bpy.data.worlds['Arm']
    wrd.world_defs = ''
    rpdat = arm.utils.get_rp()
    
    if callback != None:
        callback()
    
    # Traverse world node tree
    parsed = False
    if world.node_tree != None:
        output_node = node_utils.get_node_by_type(world.node_tree, 'OUTPUT_WORLD')
        if output_node != None:
            parse_world_output(world, output_node)
            parsed = True
    if parsed == False:
        solid_mat = rpdat.arm_material_model == 'Solid'
        if rpdat.arm_irradiance and not solid_mat:
            wrd.world_defs += '_Irr'
        c = world.color
        world.arm_envtex_color = [c[0], c[1], c[2], 1.0]
        world.arm_envtex_strength = 1.0
    
    # Clear to color if no texture or sky is provided
    if '_EnvSky' not in wrd.world_defs and '_EnvTex' not in wrd.world_defs:
        if '_EnvImg' not in wrd.world_defs:
            wrd.world_defs += '_EnvCol'
        # Irradiance json file name
        world.arm_envtex_name = wname
        world.arm_envtex_irr_name = wname
        write_probes.write_color_irradiance(wname, world.arm_envtex_color)

    # film_transparent
    if bpy.context.scene != None and hasattr(bpy.context.scene.render, 'film_transparent') and bpy.context.scene.render.film_transparent:
        wrd.world_defs += '_EnvTransp'
        wrd.world_defs += '_EnvCol'

    # Clouds enabled
    if rpdat.arm_clouds:
        wrd.world_defs += '_EnvClouds'

    if '_EnvSky' in wrd.world_defs or '_EnvTex' in wrd.world_defs or '_EnvImg' in wrd.world_defs or '_EnvClouds' in wrd.world_defs:
        wrd.world_defs += '_EnvStr'

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
    if node.type == 'TEX_ENVIRONMENT' and node.image != None:

        image = node.image
        filepath = image.filepath
        
        if image.packed_file == None and not os.path.isfile(arm.utils.asset_path(filepath)):
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

        if image.packed_file != None:
            # Extract packed data
            unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + tex_file
            filepath = unpack_filepath

            if do_convert:
                if not os.path.isfile(unpack_filepath):
                    arm.utils.unpack_image(image, unpack_filepath, file_format=target_format)

            elif os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
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
        wrd.world_defs += '_EnvTex'
        # Append LDR define
        if disable_hdr:
            wrd.world_defs += '_EnvLDR'
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
        
        wrd.world_defs += '_EnvSky'
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
