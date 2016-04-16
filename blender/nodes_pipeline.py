import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import json
import platform
import subprocess
	
class CGPipelineTree(NodeTree):
	'''Pipeline nodes'''
	bl_idname = 'CGPipelineTreeType'
	bl_label = 'CG Pipeline Node Tree'
	bl_icon = 'GAME'

class CGPipelineTreeNode:
	@classmethod
	def poll(cls, ntree):
		return ntree.bl_idname == 'CGPipelineTreeType'
		
class DrawGeometryNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawGeometryNodeType'
	bl_label = 'Draw Geometry'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Context")
		# self.inputs.new('NodeSocketBool', "Bind World")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class ClearTargetNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'ClearTargetNodeType'
	bl_label = 'Clear Target'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketBool', "Color")
		self.inputs.new('NodeSocketBool', "Depth")
		self.inputs.new('NodeSocketBool', "Stencil")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class SetTargetNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'SetTargetNodeType'
	bl_label = 'Set Target'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketShader', "Target")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class TargetNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'TargetNodeType'
	bl_label = 'Target'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketString', "ID")
		self.inputs.new('NodeSocketInt', "Width")
		self.inputs.new('NodeSocketInt', "Height")
		self.inputs.new('NodeSocketInt', "Color Buffers")
		self.inputs.new('NodeSocketBool', "Depth Buffer")
		self.inputs.new('NodeSocketBool', "Stencil Buffer")
		self.inputs.new('NodeSocketString', "Format")
		self.inputs.new('NodeSocketBool', "Ping Pong")

		self.outputs.new('NodeSocketShader', "Target")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class FramebufferNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'FramebufferNodeType'
	bl_label = 'Framebuffer'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.outputs.new('NodeSocketShader', "Target")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

class BindTargetNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'BindTargetNodeType'
	bl_label = 'Bind Target'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketShader', "Target")
		self.inputs.new('NodeSocketString', "Constant")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

class DrawMaterialQuadNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawMaterialQuadNodeType'
	bl_label = 'Draw Material Quad'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Material Context")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class DrawQuadNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawQuadNodeType'
	bl_label = 'Draw Quad'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Shader Context")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class DrawWorldNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawWorldNodeType'
	bl_label = 'Draw World'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

# Helper nodes
class QuadPassNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'QuadPassNodeType'
	bl_label = 'Quad Pass'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketShader', "Target")
		self.inputs.new('NodeSocketString', "Shader Context")
		self.inputs.new('NodeSocketShader', "Bind 1")
		self.inputs.new('NodeSocketString', "Constant")
		self.inputs.new('NodeSocketShader', "Bind 2")
		self.inputs.new('NodeSocketString', "Constant")
		self.inputs.new('NodeSocketShader', "Bind 3")
		self.inputs.new('NodeSocketString', "Constant")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MyPipelineNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'

class MyPassNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'

node_categories = [
	MyPipelineNodeCategory("PIPELINENODES", "Pipeline", items=[
		NodeItem("DrawGeometryNodeType"),
		NodeItem("ClearTargetNodeType"),
		NodeItem("SetTargetNodeType"),
		NodeItem("BindTargetNodeType"),
		NodeItem("DrawMaterialQuadNodeType"),
		NodeItem("DrawQuadNodeType"),
		NodeItem("DrawWorldNodeType"),
		NodeItem("TargetNodeType"),
		NodeItem("FramebufferNodeType"),
		]),
	MyPassNodeCategory("PASSNODES", "Pass", items=[
		NodeItem("QuadPassNodeType"),
		]),
]
	

def reload_blend_data():
	if bpy.data.node_groups.get('forward_pipeline') == None:
		load_library()
		pass

def load_library():
	haxelib_path = "haxelib"
	if platform.system() == 'Darwin':
		haxelib_path = "/usr/local/bin/haxelib"

	output = subprocess.check_output([haxelib_path + " path cyclesgame"], shell=True)
	output = str(output).split("\\n")[0].split("'")[1]
	data_path = output[:-8] + "blender/data/data.blend" # Remove 'Sources/' from haxelib path

	with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
		data_to.node_groups = ['forward_pipeline', 'forward_pipeline_noshadow', 'deferred_pipeline', 'pathtrace_pipeline', 'PBR']
	
	# TODO: cannot use for loop
	# TODO: import pbr group separately, no need for fake user
	bpy.data.node_groups['forward_pipeline'].use_fake_user = True
	bpy.data.node_groups['forward_pipeline_noshadow'].use_fake_user = True
	bpy.data.node_groups['deferred_pipeline'].use_fake_user = True
	bpy.data.node_groups['pathtrace_pipeline'].use_fake_user = True
	bpy.data.node_groups['PBR'].use_fake_user = True

def register():
	bpy.utils.register_module(__name__)
	try:
		nodeitems_utils.register_node_categories("CG_PIPELINE_NODES", node_categories)
		reload_blend_data()
	except:
		pass

def unregister():
	nodeitems_utils.unregister_node_categories("CG_PIPELINE_NODES")
	bpy.utils.unregister_module(__name__)


# Generating pipeline resources
class Object:
	def to_JSON(self):
		# return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def buildNodeTrees(shader_references, asset_references):
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('Assets/generated/pipelines'):
		os.makedirs('Assets/generated/pipelines')
	
	# Export selected pipeline
	# node_group.bl_idname == 'CGPipelineTreeType'
	node_group = bpy.data.node_groups[bpy.data.cameras[0].pipeline_path]
	buildNodeTree(node_group, shader_references, asset_references)

def buildNodeTree(node_group, shader_references, asset_references):
	output = Object()
	res = Object()
	output.pipeline_resources = [res]
	
	path = 'Assets/generated/pipelines/'
	node_group_name = node_group.name.replace('.', '_')
	
	res.id = node_group_name
	res.render_targets = get_render_targets(node_group)
	res.stages = []
	
	rn = getRootNode(node_group)
	if rn == None:
		return
	
	# Used to merge bind target nodes into one stage	
	last_bind_target = None
	
	buildNode(res, rn, node_group, last_bind_target, shader_references, asset_references)

	with open(path + node_group_name + '.json', 'w') as f:
			f.write(output.to_JSON())

def make_set_target(stage, node_group, node, target_index=1):
	stage.command = 'set_target'
	targetNode = findNodeByLink(node_group, node, node.inputs[target_index])
	if targetNode.bl_idname == 'TargetNodeType':
		postfix = ''
		if targetNode.inputs[7].default_value == True:
			if make_set_target.pong_target_stage != None:
				make_set_target.pong = not make_set_target.pong
			if make_set_target.pong == True:
				postfix = '_pong'
			make_set_target.pong_target_stage = stage
			make_set_target.pong_target_param_index = len(stage.params)		
		else:
			make_set_target.pong_target_stage = None
		targetId = targetNode.inputs[0].default_value + postfix
	else: # Framebuffer
		if make_set_target.pong_target_stage != None:
			make_set_target.pong = not make_set_target.pong
		targetId = ''
	stage.params.append(targetId)
make_set_target.pong_target_stage = None
make_set_target.pong_target_param_index = 0
make_set_target.pong = False

def make_clear_target(stage, node_group, node):
	stage.command = 'clear_target'
	if node.inputs[1].default_value == True:
		stage.params.append('color')
	if node.inputs[2].default_value == True:
		stage.params.append('depth')
	if node.inputs[3].default_value == True:
		stage.params.append('stencil')

def make_draw_geometry(stage, node_group, node):
	stage.command = 'draw_geometry'
	stage.params.append(node.inputs[1].default_value) # Context

def make_bind_target(stage, node_group, node, target_index=1, constant_index=2):
	stage.command = 'bind_target'
	targetNode = findNodeByLink(node_group, node, node.inputs[target_index])
	if targetNode.bl_idname == 'TargetNodeType':			
		postfix = ''
		if targetNode.inputs[7].default_value == True:
			if make_set_target.pong_target_stage != None:
				if make_set_target.pong == False:
					postfix = '_pong'
		targetId = targetNode.inputs[0].default_value + postfix
	stage.params.append(targetId)
	stage.params.append(node.inputs[constant_index].default_value)

def make_draw_material_quad(stage, node_group, node, shader_references, asset_references, context_index=1):
	stage.command = 'draw_material_quad'
	material_context = node.inputs[context_index].default_value
	stage.params.append(material_context)
	# Include resource and shaders
	res_name = material_context.rsplit('/', 1)[1]
	asset_references.append('compiled/ShaderResources/' + res_name + '/' + res_name + '.json')
	shader_references.append('compiled/Shaders/' + res_name + '/' + res_name)

def make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=1):
	stage.command = 'draw_shader_quad'
	shader_context = node.inputs[context_index].default_value
	stage.params.append(shader_context)
	# Include resource and shaders
	res_name = shader_context.split('/', 1)[0]
	asset_references.append('compiled/ShaderResources/' + res_name + '/' + res_name + '.json')
	shader_references.append('compiled/Shaders/' + res_name + '/' + res_name)

def make_draw_world(stage, node_group, node):
	stage.command = 'draw_material_quad'
	wname = bpy.data.worlds[0].name
	stage.params.append(wname + '_material/' + wname + '_material/env_map') # Only one world for now

def buildNode(res, node, node_group, last_bind_target, shader_references, asset_references):
	stage = Object()
	stage.params = []
	
	append_stage = True
	
	if node.bl_idname == 'SetTargetNodeType':
		last_bind_target = None
		make_set_target(stage, node_group, node)

	elif node.bl_idname == 'ClearTargetNodeType':
		make_clear_target(stage, node_group, node)
			
	elif node.bl_idname == 'DrawGeometryNodeType':
		make_draw_geometry(stage, node_group, node)
		
	elif node.bl_idname == 'BindTargetNodeType':
		if last_bind_target is not None:
			stage = last_bind_target
			append_stage = False
		last_bind_target = stage
		make_bind_target(stage, node_group, node)
		
	elif node.bl_idname == 'DrawMaterialQuadNodeType':
		make_draw_material_quad(stage, node_group, node, shader_references, asset_references)
		
	elif node.bl_idname == 'DrawQuadNodeType':
		make_draw_quad(stage, node_group, node, shader_references, asset_references)
	
	elif node.bl_idname == 'DrawWorldNodeType':
		make_draw_world(stage, node_group, node)
	
	elif node.bl_idname == 'QuadPassNodeType':
		append_stage = False
		# Set target
		if node.inputs[1].is_linked:
			last_bind_target = None
			make_set_target(stage, node_group, node)
			res.stages.append(stage)
		# Bind targets
		stage = Object()
		stage.params = []
		last_bind_target = stage
		
		bind_target_used = False		
		if node.inputs[3].is_linked:
			bind_target_used = True
			make_bind_target(stage, node_group, node, target_index=3, constant_index=4)
		if node.inputs[5].is_linked:
			bind_target_used = True
			make_bind_target(stage, node_group, node, target_index=5, constant_index=6)
		if node.inputs[7].is_linked:
			bind_target_used = True
			make_bind_target(stage, node_group, node, target_index=7, constant_index=8)
		if bind_target_used:
			res.stages.append(stage)
			stage = Object()
			stage.params = []
		# Draw quad
		make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=2)
		res.stages.append(stage)
	
	if append_stage:
		res.stages.append(stage)
	
	# Build next stage
	if node.outputs[0].is_linked:
		stageNode = findNodeByLinkFrom(node_group, node, node.outputs[0])
		buildNode(res, stageNode, node_group, last_bind_target, shader_references, asset_references)
			
def findNodeByLink(node_group, to_node, inp):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == inp:
			return link.from_node
			
def findNodeByLinkFrom(node_group, from_node, outp):
	for link in node_group.links:
		if link.from_node == from_node and link.from_socket == outp:
			return link.to_node
	
def getRootNode(node_group):
	# First node with empty stage input
	for n in node_group.nodes:
		if len(n.inputs) > 0 and n.inputs[0].is_linked == False and n.inputs[0].name == 'Stage':
			return n

def make_render_target(n, postfix=''):
	target = Object()
	target.id = n.inputs[0].default_value + postfix
	target.width = n.inputs[1].default_value
	target.height = n.inputs[2].default_value
	target.color_buffers = n.inputs[3].default_value
	target.depth_buffer = n.inputs[4].default_value
	target.stencil_buffer = n.inputs[5].default_value
	target.format = n.inputs[6].default_value
	return target

def get_render_targets(node_group):
	render_targets = []
	for n in node_group.nodes:
		if n.bl_idname == 'TargetNodeType':
			target = make_render_target(n)
			render_targets.append(target)
			if n.inputs[7].default_value == True: # Ping-pong
				target = make_render_target(n, '_pong')
				render_targets.append(target)
	return render_targets
