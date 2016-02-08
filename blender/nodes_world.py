import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import json

def register():
	pass
	#bpy.utils.register_module(__name__)

def unregister():
	pass
	#bpy.utils.unregister_module(__name__)

# Generating world resources
class Object:
	def to_JSON(self):
		# return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def buildNodeTrees():
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('Assets/generated/materials'):
		os.makedirs('Assets/generated/materials')
	
	# Export world nodes
	for world in bpy.data.worlds:
		buildNodeTree(world.name, world.node_tree)

def buildNodeTree(world_name, node_group):
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
	for node in node_group.nodes:
		if node.bl_idname == 'ShaderNodeTexEnvironment': # Just look for env texture for now
			texture.name = node.image.name.rsplit('.', 1)[0] # Remove extension

	with open(path + material_name + '.json', 'w') as f:
		f.write(output.to_JSON())
