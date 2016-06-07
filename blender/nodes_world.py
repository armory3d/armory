import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import json
import write_probes

def register():
	pass
	#bpy.utils.register_module(__name__)

def unregister():
	pass
	#bpy.utils.unregister_module(__name__)

# Generating world resources
class Object:
	def to_JSON(self):
		if bpy.data.worlds[0].CGMinimize == True:
			return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
		else:
			return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def buildNodeTrees(shader_references, asset_references):
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('Assets/generated/materials'):
		os.makedirs('Assets/generated/materials')
	
	# Export world nodes
	for world in bpy.data.worlds:
		buildNodeTree(world.name, world.node_tree, shader_references, asset_references)

def buildNodeTree(world_name, node_group, shader_references, asset_references):
	output = Object()
	res = Object()
	output.material_resources = [res]
	
	path = 'Assets/generated/materials/'
	material_name = world_name.replace('.', '_') + '_material'
	
	res.id = material_name
	res.shader = 'env_map/env_map'
	context = Object()
	res.contexts = [context]
	
	context.id = 'env_map'
	context.bind_constants = []
	texture = Object()
	context.bind_textures = [texture]
	
	texture.id = 'envmap'
	texture.name = ''
	
	bpy.data.worlds[0].world_defs = ''
	
	for node in node_group.nodes:
		# Env map included
		if node.type == 'TEX_ENVIRONMENT': # Just look for env texture for now
			image_name =  node.image.name # With extension
			texture.name = image_name.rsplit('.', 1)[0] # Remove extension
			# Add resources to khafie
			asset_references.append('compiled/ShaderResources/env_map/env_map.json')
			shader_references.append('compiled/Shaders/env_map/env_map')
			
			# Generate prefiltered envmaps
			bpy.data.cameras[0].world_envtex_name = texture.name
			disable_hdr = image_name.endswith('.jpg')
			mip_count = bpy.data.cameras[0].world_envtex_num_mips
			mip_count = write_probes.write_probes(image_name, disable_hdr, mip_count)
			bpy.data.cameras[0].world_envtex_num_mips = mip_count
			
			# Append envtex define
			bpy.data.worlds[0].world_defs += '_EnvTex'
			# Append LDR define
			if disable_hdr:
				bpy.data.worlds[0].world_defs += '_LDR'
			
		# Extract environment strength
		if node.type == 'BACKGROUND':
			bpy.data.cameras[0].world_envtex_strength = node.inputs[1].default_value
		if node.type == 'TEX_SKY':
			bpy.data.worlds[0].world_defs += '_EnvSky'
	
	# Enable probes
	num_probes = 0
	for cam in bpy.data.cameras:
		if cam.is_probe:
			num_probes += 1
			bpy.data.worlds[0].world_defs += '_Probe' + str(num_probes)

	with open(path + material_name + '.json', 'w') as f:
		f.write(output.to_JSON())
