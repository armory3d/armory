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
	if not os.path.exists('compiled/Assets/materials'):
		os.makedirs('compiled/Assets/materials')
	
	# Export world nodes
	world_outputs = []
	for world in bpy.data.worlds:
		output = buildNodeTree(world.name, world.node_tree)
		world_outputs.append(output)
	return world_outputs

def buildNodeTree(world_name, node_group):
	output = {}
	res = {}
	output['material_resources'] = [res]
	res['id'] = world_name.replace('.', '_') + '_material'
	context = {}
	res['contexts'] = [context]
	context['id'] = 'env_map'
	context['bind_constants'] = []
	context['bind_textures'] = []
	
	bpy.data.worlds[0].world_defs = ''
	
	# Traverse world node tree
	output_node = get_output_node(node_group)
	if output_node != None:
		parse_world_output(node_group, output_node, context)
	
	# Clear to color if no texture or sky is provided
	world_defs = bpy.data.worlds[0].world_defs
	if '_EnvSky' not in world_defs and '_EnvTex' not in world_defs:
		bpy.data.worlds[0].world_defs += '_EnvCol'
		# Irradiance json file name
		base_name = bpy.data.worlds[0].name
		bpy.data.cameras[0].world_envtex_name = base_name
		write_probes.write_color_irradiance(base_name, bpy.data.cameras[0].world_envtex_color)

	# Clouds enabled
	if bpy.data.worlds[0].generate_clouds:
		bpy.data.worlds[0].world_defs += '_EnvClouds'

	# Shadows disabled
	if bpy.data.worlds[0].generate_shadows == False:
		bpy.data.worlds[0].world_defs += '_NoShadows'

	# Enable probes
	for cam in bpy.data.cameras:
		if cam.is_probe:
			bpy.data.worlds[0].world_defs += '_Probes'

	# Data will be written after pipeline has been processed to gather all defines
	return output

def write_output(output, asset_references, shader_references):
	# Add resources to khafie
	dir_name = 'env_map'
	# Append world defs
	res_name = 'env_map' + bpy.data.worlds[0].world_defs
	# Reference correct shader context
	res = output['material_resources'][0]
	res['shader'] = res_name + '/' + res_name
	asset_references.append('compiled/ShaderResources/' + dir_name + '/' + res_name + '.arm')
	shader_references.append('compiled/Shaders/' + dir_name + '/' + res_name)

	# Write material json
	path = 'compiled/Assets/materials/'
	asset_path = path + res['id'] + '.arm'
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
		envmap_strength_const['id'] = 'envmapStrength'
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
		texture['id'] = 'envmap'
		image_name = node.image.name # With extension
		texture['name'] = image_name.rsplit('.', 1)[0] # Remove extension	
		# Generate prefiltered envmaps
		generate_radiance = bpy.data.worlds[0].generate_radiance
		bpy.data.cameras[0].world_envtex_name = texture['name']
		disable_hdr = image_name.endswith('.jpg')
		mip_count = bpy.data.cameras[0].world_envtex_num_mips
		
		mip_count = write_probes.write_probes(node.image.filepath, disable_hdr, mip_count, generate_radiance=generate_radiance)
		
		bpy.data.cameras[0].world_envtex_num_mips = mip_count
		# Append envtex define
		bpy.data.worlds[0].world_defs += '_EnvTex'
		# Append LDR define
		if disable_hdr:
			bpy.data.worlds[0].world_defs += '_EnvLDR'
		# Append radiance degine
		if generate_radiance:
			bpy.data.worlds[0].world_defs += '_Rad'
	
	# Append sky define
	elif node.type == 'TEX_SKY':
		bpy.data.worlds[0].world_defs += '_EnvSky'
		# Append sky properties to material
		const = {}
		const['id'] = 'sunDirection'
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

		# Adjust strength to match Cycles
		envmap_strength_const['float'] *= 0.25
