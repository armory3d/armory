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
		self.inputs.new('NodeSocketBool', "Depth")
		self.inputs.new('NodeSocketString', "Format")

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

class DrawQuadNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawQuadNodeType'
	bl_label = 'Draw Quad'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Material Context")

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

node_categories = [
	MyPipelineNodeCategory("PIPELINENODES", "Pipeline Nodes", items=[
		NodeItem("DrawGeometryNodeType"),
		NodeItem("ClearTargetNodeType"),
		NodeItem("SetTargetNodeType"),
		NodeItem("BindTargetNodeType"),
		NodeItem("DrawQuadNodeType"),
		NodeItem("DrawWorldNodeType"),
		NodeItem("TargetNodeType"),
		NodeItem("FramebufferNodeType"),
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
		data_to.node_groups = ['forward_pipeline', 'forward_pipeline_noshadow', 'deferred_pipeline', 'CG PBR']
	
	# TODO: cannot use for loop
	# TODO: import pbr group separately, no need for fake user
	bpy.data.node_groups['forward_pipeline'].use_fake_user = True
	bpy.data.node_groups['forward_pipeline_noshadow'].use_fake_user = True
	bpy.data.node_groups['deferred_pipeline'].use_fake_user = True
	bpy.data.node_groups['CG PBR'].use_fake_user = True

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

def buildNodeTrees():
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('Assets/generated/pipelines'):
		os.makedirs('Assets/generated/pipelines')
	
	# Export pipelines
	for node_group in bpy.data.node_groups:
		if node_group.bl_idname == 'CGPipelineTreeType': # Build only render pipeline trees
			buildNodeTree(node_group)

def buildNodeTree(node_group):
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
	buildNode(res, rn, node_group)

	with open(path + node_group_name + '.json', 'w') as f:
			f.write(output.to_JSON())

def buildNode(res, node, node_group):
	stage = Object()
	stage.params = []
	
	if node.bl_idname == 'SetTargetNodeType':
		stage.command = 'set_target'
		targetNode = findNodeByLink(node_group, node, node.inputs[1])
		if targetNode.bl_idname == 'TargetNodeType':
			targetId = targetNode.inputs[0].default_value
		else: # Framebuffer
			targetId = ''
		stage.params.append(targetId)
		
	elif node.bl_idname == 'ClearTargetNodeType':
		stage.command = 'clear_target'
		if node.inputs[1].default_value == True:
			stage.params.append('color')
		if node.inputs[2].default_value == True:
			stage.params.append('depth')
			
	elif node.bl_idname == 'DrawGeometryNodeType':
		stage.command = 'draw_geometry'
		stage.params.append(node.inputs[1].default_value) # Context
		
	elif node.bl_idname == 'BindTargetNodeType':
		stage.command = 'bind_target'
		targetNode = findNodeByLink(node_group, node, node.inputs[1])
		if targetNode.bl_idname == 'TargetNodeType':
			targetId = targetNode.inputs[0].default_value
		stage.params.append(targetId)
		stage.params.append(node.inputs[2].default_value)
		
	elif node.bl_idname == 'DrawQuadNodeType':
		stage.command = 'draw_quad'
		material_context = node.inputs[1].default_value
		stage.params.append(material_context)
	
	elif node.bl_idname == 'DrawWorldNodeType':
		stage.command = 'draw_quad'
		wname = bpy.data.worlds[0].name
		stage.params.append(wname + '_material/' + wname + '_material/env_map') # Only one world for now
	
	res.stages.append(stage)
	
	# Build next stage
	if node.outputs[0].is_linked:
		stageNode = findNodeByFromLink(node_group, node, node.outputs[0])
		buildNode(res, stageNode, node_group)
			
def findNodeByLink(node_group, to_node, inp):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == inp:
			return link.from_node
			
def findNodeByFromLink(node_group, from_node, outp):
	for link in node_group.links:
		if link.from_node == from_node and link.from_socket == outp:
			return link.to_node
	
def getRootNode(node_group):
	# First node with empty stage input
	for n in node_group.nodes:
		if len(n.inputs) > 0 and n.inputs[0].is_linked == False and n.inputs[0].name == 'Stage':
			return n

def get_render_targets(node_group):
	render_targets = []
	for n in node_group.nodes:
		if n.bl_idname == 'TargetNodeType':
			target = Object()
			target.id = n.inputs[0].default_value
			target.width = n.inputs[1].default_value
			target.height = n.inputs[2].default_value
			target.color_buffers = n.inputs[3].default_value
			target.depth = n.inputs[4].default_value
			target.format = n.inputs[5].default_value
			render_targets.append(target)
	return render_targets
