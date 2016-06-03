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
		
class DrawDecalsNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DrawDecalsNodeType'
	bl_label = 'Draw Decals'
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
		self.inputs.new('NodeSocketColor', "Value")
		self.inputs.new('NodeSocketBool', "Depth")
		self.inputs.new('NodeSocketFloat', "Value")
		self.inputs[4].default_value = 1.0
		self.inputs.new('NodeSocketBool', "Stencil")
		self.inputs.new('NodeSocketInt', "Value")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

class BeginNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'BeginNodeType'
	bl_label = 'Begin'
	bl_icon = 'SOUND'
	
	def init(self, context):
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
		self.inputs.new('NodeSocketShader', "Depth Buffer")
		self.inputs.new('NodeSocketString', "Format")
		self.inputs.new('NodeSocketBool', "Ping Pong")

		self.outputs.new('NodeSocketShader', "Target")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

class DebthBufferNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'DepthBufferNodeType'
	bl_label = 'Depth Buffer'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketString', "ID")
		self.inputs.new('NodeSocketBool', "Stencil")
		
		self.outputs.new('NodeSocketShader', "Target")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")

class GBufferNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'GBufferNodeType'
	bl_label = 'GBuffer'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Target 0")
		self.inputs.new('NodeSocketShader', "Target 1")
		self.inputs.new('NodeSocketShader', "Target 2")
		self.inputs.new('NodeSocketShader', "Target 3")
		self.inputs.new('NodeSocketShader', "Target 4")

		self.outputs.new('NodeSocketShader', "Targets")

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

class CallFunctionNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'CallFunctionNodeType'
	bl_label = 'Call Function'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Function")

		self.outputs.new('NodeSocketShader', "Stage")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
	
class BranchFunctionNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'BranchFunctionNodeType'
	bl_label = 'Branch Function'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketString', "Function")

		self.outputs.new('NodeSocketShader', "True")
		self.outputs.new('NodeSocketShader', "False")

	def copy(self, node):
		print("Copying from node ", node)

	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class MergeStagesNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'MergeStagesNodeType'
	bl_label = 'Merge Stages'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.inputs.new('NodeSocketShader', "Stage")
		self.inputs.new('NodeSocketShader', "Stage")

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

# Pass nodes
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

# Constant nodes
class ScreenNode(Node, CGPipelineTreeNode):
	'''A custom node'''
	bl_idname = 'ScreenNodeType'
	bl_label = 'Screen'
	bl_icon = 'SOUND'
	
	def init(self, context):
		self.outputs.new('NodeSocketInt', "Width")
		self.outputs.new('NodeSocketInt', "Height")

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

class MyTargetNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'

class MyPassNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'
		
class MyConstantNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'

class MyLogicNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGPipelineTreeType'

node_categories = [
	MyPipelineNodeCategory("PIPELINENODES", "Pipeline", items=[
		NodeItem("BeginNodeType"),
		NodeItem("DrawGeometryNodeType"),
		NodeItem("DrawDecalsNodeType"),
		NodeItem("ClearTargetNodeType"),
		NodeItem("SetTargetNodeType"),
		NodeItem("BindTargetNodeType"),
		NodeItem("DrawMaterialQuadNodeType"),
		NodeItem("DrawQuadNodeType"),
		NodeItem("DrawWorldNodeType"),
	]),
	MyTargetNodeCategory("TARGETNODES", "Target", items=[
		NodeItem("TargetNodeType"),
		NodeItem("DepthBufferNodeType"),
		NodeItem("GBufferNodeType"),
		NodeItem("FramebufferNodeType"),
	]),
	MyPassNodeCategory("PASSNODES", "Pass", items=[
		NodeItem("QuadPassNodeType"),
		# Prebuilt passes here
	]),
	MyConstantNodeCategory("CONSTANTNODES", "Constant", items=[
		NodeItem("ScreenNodeType"),
	]),
	MyLogicNodeCategory("LOGICNODES", "Logic", items=[
		NodeItem("CallFunctionNodeType"),
		NodeItem("BranchFunctionNodeType"),
		NodeItem("MergeStagesNodeType"),
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
	res.render_targets, res.depth_buffers = get_render_targets(node_group)
	res.stages = []
	
	rn = getRootNode(node_group)
	if rn == None:
		return
	
	# Used to merge bind target nodes into one stage	
	last_bind_target = None
	
	buildNode(res.stages, rn, node_group, last_bind_target, shader_references, asset_references)

	with open(path + node_group_name + '.json', 'w') as f:
			f.write(output.to_JSON())

def make_set_target(stage, node_group, node, currentNode=None, target_index=1):
	if currentNode == None:
		currentNode = node
	
	stage.command = 'set_target'
	currentNode = findNodeByLink(node_group, currentNode, currentNode.inputs[target_index])
	
	if currentNode.bl_idname == 'TargetNodeType':
		targetId = currentNode.inputs[0].default_value
		stage.params.append(targetId)
	
	elif currentNode.bl_idname == 'GBufferNodeType':
		# Set all linked targets
		for i in range(0, 5):
			if currentNode.inputs[i].is_linked:
				make_set_target(stage, node_group, node, currentNode, target_index=i)
	
	elif currentNode.bl_idname == 'NodeReroute':
		make_set_target(stage, node_group, node, currentNode, target_index=0)
	
	else: # Framebuffer
		targetId = ''
		stage.params.append(targetId)

def make_clear_target(stage, node_group, node):
	stage.command = 'clear_target'
	if node.inputs[1].default_value == True:
		stage.params.append('color')
		val = node.inputs[2].default_value
		hex = '#%02x%02x%02x%02x' % (int(val[3] * 255), int(val[0] * 255), int(val[1] * 255), int(val[2] * 255))
		stage.params.append(str(hex))
	if node.inputs[3].default_value == True:
		stage.params.append('depth')
		val = node.inputs[4].default_value
		stage.params.append(str(val))
	if node.inputs[5].default_value == True:
		stage.params.append('stencil')
		val = node.inputs[6].default_value
		stage.params.append(str(val))

def make_draw_geometry(stage, node_group, node):
	stage.command = 'draw_geometry'
	stage.params.append(node.inputs[1].default_value) # Context
	
def make_draw_decals(stage, node_group, node, shader_references, asset_references):
	stage.command = 'draw_decals'
	context = node.inputs[1].default_value
	stage.params.append(context) # Context
	bpy.data.cameras[0].last_decal_context = context

def make_bind_target(stage, node_group, node, currentNode=None, target_index=1, constant_index=2):
	if currentNode == None:
		currentNode = node
		
	stage.command = 'bind_target'
	
	link = findLink(node_group, currentNode, currentNode.inputs[target_index])
	currentNode = link.from_node
	
	if currentNode.bl_idname == 'NodeReroute':
		make_bind_target(stage, node_group, node, currentNode, target_index=0, constant_index=constant_index)
	
	elif currentNode.bl_idname == 'GBufferNodeType':
		for i in range(0, 5):
			if currentNode.inputs[i].is_linked:
				targetNode = findNodeByLink(node_group, currentNode, currentNode.inputs[i])
				targetId = targetNode.inputs[0].default_value
				# if i == 0 and targetNode.inputs[3].default_value == True: # Depth
				if targetNode.inputs[3].is_linked: # Depth
					db_node = findNodeByLink(node_group, targetNode, targetNode.inputs[3])
					db_id = db_node.inputs[0].default_value
					stage.params.append('_' + db_id)
					stage.params.append(node.inputs[constant_index].default_value + 'D')
				stage.params.append(targetId) # Color buffer
				stage.params.append(node.inputs[constant_index].default_value + str(i))
	
	elif currentNode.bl_idname == 'TargetNodeType':		
		targetId = currentNode.inputs[0].default_value
		stage.params.append(targetId)
		stage.params.append(node.inputs[constant_index].default_value)
		
	elif currentNode.bl_idname == 'DepthBufferNodeType':
		targetId = '_' + currentNode.inputs[0].default_value
		stage.params.append(targetId)
		stage.params.append(node.inputs[constant_index].default_value)

def make_draw_material_quad(stage, node_group, node, shader_references, asset_references, context_index=1):
	stage.command = 'draw_material_quad'
	material_context = node.inputs[context_index].default_value
	stage.params.append(material_context)
	# Include resource and shaders
	scon = shader_context.split('/')
	dir_name = scon[0]
	# Append world defs
	res_name = scon[1]
	asset_references.append('compiled/ShaderResources/' + dir_name + '/' + res_name + '.json')
	shader_references.append('compiled/Shaders/' + dir_name + '/' + res_name)

def make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=1):
	stage.command = 'draw_shader_quad'
	# Append world defs to get proper context
	world_defs = bpy.data.worlds[0].world_defs
	shader_context = node.inputs[context_index].default_value
	scon = shader_context.split('/')
	stage.params.append(scon[0] + world_defs + '/' + scon[1] + world_defs + '/' + scon[2])
	# Include resource and shaders
	dir_name = scon[0]
	# Append world defs
	res_name = scon[1] + world_defs
	asset_references.append('compiled/ShaderResources/' + dir_name + '/' + res_name + '.json')
	shader_references.append('compiled/Shaders/' + dir_name + '/' + res_name)

def make_draw_world(stage, node_group, node):
	stage.command = 'draw_material_quad'
	wname = bpy.data.worlds[0].name
	stage.params.append(wname + '_material/' + wname + '_material/env_map') # Only one world for now

def make_call_function(stage, node_group, node):
	stage.command = 'call_function'
	stage.params.append(node.inputs[1].default_value)

def make_branch_function(stage, node_group, node):
	make_call_function(stage, node_group, node)
	
def process_call_function(stage, stages, node, node_group, last_bind_target, shader_references, asset_references):
	# Step till merge node
	stage.returns_true = []
	if node.outputs[0].is_linked:
		stageNode = findNodeByLinkFrom(node_group, node, node.outputs[0])
		buildNode(stage.returns_true, stageNode, node_group, last_bind_target, shader_references, asset_references)
	
	stage.returns_false = [] 
	if node.outputs[1].is_linked:
		stageNode = findNodeByLinkFrom(node_group, node, node.outputs[1])
		margeNode = buildNode(stage.returns_false, stageNode, node_group, last_bind_target, shader_references, asset_references)
	
	# Continue using top level stages after merge node
	afterMergeNode = findNodeByLinkFrom(node_group, margeNode, margeNode.outputs[0])
	buildNode(stages, afterMergeNode, node_group, last_bind_target, shader_references, asset_references)

# Returns merge node
def buildNode(stages, node, node_group, last_bind_target, shader_references, asset_references):
	stage = Object()
	stage.params = []
	
	append_stage = True
	
	if node.bl_idname == 'MergeStagesNodeType':
		return node
	
	elif node.bl_idname == 'SetTargetNodeType':
		last_bind_target = None
		make_set_target(stage, node_group, node)

	elif node.bl_idname == 'ClearTargetNodeType':
		make_clear_target(stage, node_group, node)
			
	elif node.bl_idname == 'DrawGeometryNodeType':
		make_draw_geometry(stage, node_group, node)
		
	elif node.bl_idname == 'DrawDecalsNodeType':
		make_draw_decals(stage, node_group, node, shader_references, asset_references)
		
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
		
	elif node.bl_idname == 'BranchFunctionNodeType':
		make_branch_function(stage, node_group, node)
		stages.append(stage)
		process_call_function(stage, stages, node, node_group, last_bind_target, shader_references, asset_references)
		return
		
	elif node.bl_idname == 'CallFunctionNodeType':
		make_call_function(stage, node_group, node)
	
	elif node.bl_idname == 'QuadPassNodeType':
		append_stage = False
		# Set target
		if node.inputs[1].is_linked:
			last_bind_target = None
			make_set_target(stage, node_group, node)
			stages.append(stage)
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
			stages.append(stage)
			stage = Object()
			stage.params = []
		# Draw quad
		make_draw_quad(stage, node_group, node, shader_references, asset_references, context_index=2)
		stages.append(stage)
	
	if append_stage:
		stages.append(stage)
	
	# Build next stage
	if node.outputs[0].is_linked:
		stageNode = findNodeByLinkFrom(node_group, node, node.outputs[0])
		buildNode(stages, stageNode, node_group, last_bind_target, shader_references, asset_references)
			
def findNodeByLink(node_group, to_node, inp):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == inp:
			return link.from_node

def findLink(node_group, to_node, inp):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == inp:
			return link
			
def findNodeByLinkFrom(node_group, from_node, outp):
	for link in node_group.links:
		if link.from_node == from_node and link.from_socket == outp:
			return link.to_node
	
def getRootNode(node_group):
	# Find first node linked to begin node
	for n in node_group.nodes:
		if n.bl_idname == 'BeginNodeType':
			return findNodeByLinkFrom(node_group, n, n.outputs[0])

def make_render_target(n, depth_buffer_id=None):
	target = Object()
	target.id = n.inputs[0].default_value
	target.width = n.inputs[1].default_value
	target.height = n.inputs[2].default_value
	target.format = n.inputs[4].default_value
	target.ping_pong = n.inputs[5].default_value	
	if depth_buffer_id != None:
		target.depth_buffer = depth_buffer_id
	return target

def get_render_targets(node_group):
	render_targets = []
	depth_buffers = []
	for n in node_group.nodes:
		if n.bl_idname == 'TargetNodeType':
			depth_buffer_id = None
			if n.inputs[3].is_linked:
				depth_node = findNodeByLink(node_group, n, n.inputs[3])
				depth_buffer_id = depth_node.inputs[0].default_value
				# Append depth buffer
				found = False
				for db in depth_buffers:
					if db.id == depth_buffer_id:
						found = True
						break 
				if found == False:
					db = Object()
					db.id = depth_buffer_id
					db.stencil_buffer = depth_node.inputs[1].default_value
					depth_buffers.append(db)	
			# Append target	
			target = make_render_target(n, depth_buffer_id=depth_buffer_id)
			render_targets.append(target)
	return render_targets, depth_buffers
