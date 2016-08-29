import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import json
import write_probes
import assets
import utils

def register():
	pass
	#bpy.utils.register_module(__name__)

def unregister():
	pass
	#bpy.utils.unregister_module(__name__)

def find_node(node_group, to_node, target_socket):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == target_socket:
			return link.from_node

def get_output_node(tree):
	for n in tree.nodes:
		if n.type == 'OUTPUT_WORLD':
			return n

def buildNodeTrees():
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('build/compiled/Assets/materials'):
		os.makedirs('build/compiled/Assets/materials')
	
	# Export world nodes
	world_outputs = []
	for world in bpy.data.worlds:
		output = buildNodeTree(world.name, world.node_tree)
		world_outputs.append(output)
	return world_outputs

def buildNodeTree(world_name, node_group):
	output = {}
	dat = {}
	output['material_datas'] = [dat]
	dat['name'] = world_name.replace('.', '_') + '_material'
	context = {}
	dat['contexts'] = [context]
	context['name'] = 'env'
	context['bind_constants'] = []
	context['bind_textures'] = []
	
	bpy.data.worlds[0].world_defs = ''
	
	# Traverse world node tree
	output_node = get_output_node(node_group)
	if output_node != None:
		parse_world_output(node_group, output_node, context)
	
	# Clear to color if no texture or sky is provided
	wrd = bpy.data.worlds[0]
	if '_EnvSky' not in wrd.world_defs and '_EnvTex' not in wrd.world_defs:
		wrd.world_defs += '_EnvCol'
		# Irradiance json file name
		base_name = wrd.name
		bpy.data.cameras[0].world_envtex_name = base_name
		write_probes.write_color_irradiance(base_name, bpy.data.cameras[0].world_envtex_color)

	# Clouds enabled
	if wrd.generate_clouds:
		wrd.world_defs += '_EnvClouds'

	# Shadows disabled
	if wrd.generate_shadows == False:
		wrd.world_defs += '_NoShadows'

	# Percentage closer soft shadows
	if wrd.generate_pcss:
		wrd.world_defs += '_PCSS'

	# Enable probes
	for cam in bpy.data.cameras:
		if cam.is_probe:
			wrd.world_defs += '_Probes'

	# Data will be written after pipeline has been processed to gather all defines
	return output

def write_output(output, asset_references, shader_references):
	# Add datas to khafie
	dir_name = 'env'
	# Append world defs
	wrd = bpy.data.worlds[0]
	data_name = 'env' + wrd.world_defs
	
	# Reference correct shader context
	dat = output['material_datas'][0]
	dat['shader'] = data_name + '/' + data_name
	asset_references.append('build/compiled/ShaderDatas/' + dir_name + '/' + data_name + '.arm')
	shader_references.append('build/compiled/Shaders/' + dir_name + '/' + data_name)

	# Write material json
	path = 'build/compiled/Assets/materials/'
	asset_path = path + dat['name'] + '.arm'
	utils.write_arm(asset_path, output)
	assets.add(asset_path)

def parse_world_output(node_group, node, context):
	if node.inputs[0].is_linked:
		surface_node = find_node(node_group, node, node.inputs[0])
		parse_surface(node_group, surface_node, context)
	
def parse_surface(node_group, node, context):
	# Extract environment strength
	if node.type == 'BACKGROUND':
		# Strength
		envmap_strength_const = {}
		envmap_strength_const['name'] = 'envmapStrength'
		envmap_strength_const['float'] = node.inputs[1].default_value
		context['bind_constants'].append(envmap_strength_const)
		
		if node.inputs[0].is_linked:
			color_node = find_node(node_group, node, node.inputs[0])
			parse_color(node_group, color_node, context, envmap_strength_const)

		# Cache results
		bpy.data.cameras[0].world_envtex_color = node.inputs[0].default_value
		bpy.data.cameras[0].world_envtex_strength = envmap_strength_const['float']

def parse_color(node_group, node, context, envmap_strength_const):		
	# Env map included
	if node.type == 'TEX_ENVIRONMENT':
		texture = {}
		context['bind_textures'].append(texture)
		texture['name'] = 'envmap'
		
		image = node.image
		if image.packed_file != None:
			# Extract packed data
			unpack_path = utils.get_fp() + '/build/compiled/Assets/unpacked'
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
		texture['file'] = utils.extract_filename_noext(image.filepath)
		texture['file'] = utils.safe_filename(texture['file'])

		# Generate prefiltered envmaps
		generate_radiance = bpy.data.worlds[0].generate_radiance
		bpy.data.cameras[0].world_envtex_name = texture['file']
		disable_hdr = image.filepath.endswith('.jpg')
		mip_count = bpy.data.cameras[0].world_envtex_num_mips
		
		mip_count = write_probes.write_probes(node.image.filepath, disable_hdr, mip_count, generate_radiance=generate_radiance)
		
		bpy.data.cameras[0].world_envtex_num_mips = mip_count
		# Append envtex define
		bpy.data.worlds[0].world_defs += '_EnvTex'
		# Append LDR define
		if disable_hdr:
			bpy.data.worlds[0].world_defs += '_EnvLDR'
		# Append radiance define
		if generate_radiance:
			bpy.data.worlds[0].world_defs += '_Rad'
	
	# Append sky define
	elif node.type == 'TEX_SKY':
		bpy.data.worlds[0].world_defs += '_EnvSky'
		# Append sky properties to material
		const = {}
		const['name'] = 'sunDirection'
		sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
		sun_direction[1] *= -1 # Fix Y orientation
		const['vec3'] = list(sun_direction)
		context['bind_constants'].append(const)
		
		bpy.data.cameras[0].world_envtex_sun_direction = sun_direction
		bpy.data.cameras[0].world_envtex_turbidity = node.turbidity
		bpy.data.cameras[0].world_envtex_ground_albedo = node.ground_albedo
		
		# Irradiance json file name
		base_name = bpy.data.worlds[0].name
		bpy.data.cameras[0].world_envtex_name = base_name
		
		write_probes.write_sky_irradiance(base_name)

		# Radiance
		if bpy.data.worlds[0].generate_radiance_sky and bpy.data.worlds[0].generate_radiance:
			bpy.data.worlds[0].world_defs += '_Rad'
			
			user_preferences = bpy.context.user_preferences
			addon_prefs = user_preferences.addons['armory'].preferences
			sdk_path = addon_prefs.sdk_path
			assets.add(sdk_path + 'armory/Assets/hosek/hosek_radiance.hdr')
			for i in range(0, 8):
				assets.add(sdk_path + 'armory/Assets/hosek/hosek_radiance_' + str(i) + '.hdr')
			
			bpy.data.cameras[0].world_envtex_num_mips = 8

		# Adjust strength to match Cycles
		envmap_strength_const['float'] *= 0.25
