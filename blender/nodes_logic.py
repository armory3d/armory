import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
# Implementation of custom nodes from Python
	
# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class CGTree(NodeTree):
	# Description string
	'''Logic nodes'''
	# Optional identifier string. If not explicitly defined, the python class name is used.
	bl_idname = 'CGTreeType'
	# Label for nice name display
	bl_label = 'CG Node Tree'
	# Icon identifier
	# NOTE: If no icon is defined, the node tree will not show up in the editor header!
	#     This can be used to make additional tree types for groups and similar nodes (see below)
	#     Only one base tree class is needed in the editor for selecting the general category
	bl_icon = 'GAME'

	#def update(self):
		#print("runing tree")

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class CGTreeNode:
	@classmethod
	def poll(cls, ntree):
		return ntree.bl_idname == 'CGTreeType'


# Derived from the Node base type.
class TransformNode(Node, CGTreeNode):
	# Description string
	'''A custom node'''
	# Optional identifier string. If not explicitly defined, the python class name is used.
	bl_idname = 'TransformNodeType'
	# Label for nice name display
	bl_label = '@Transform'
	# Icon identifier
	bl_icon = 'SOUND'

	# These work just like custom properties in ID data blocks
	# Extensive information can be found under
	# http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
	#objname = bpy.props.StringProperty()
	
	# Initialization function, called when a new node is created.
	# This is the most common place to create the sockets for a node, as shown below.
	# NOTE: this is not the same as the standard __init__ function in Python, which is
	#     a purely internal Python method and unknown to the node system!
	def init(self, context):
		self.inputs.new('NodeSocketVector', "Position")
		self.inputs.new('NodeSocketVector', "Rotation")
		self.inputs.new('NodeSocketVector', "Scale")

		self.inputs["Scale"].default_value = [1.0, 1.0, 1.0]

		self.outputs.new('NodeSocketString', "Transform")

	# Copy function to initialize a copied node from an existing one.
	def copy(self, node):
		print("Copying from node ", node)

	# Free function to clean up on removal.
	def free(self):
		print("Removing node ", self, ", Goodbye!")

	# Additional buttons displayed on the node.
	#def draw_buttons(self, context, layout):
		#layout.prop_search(self, "objname", context.scene, "objects", text = "")

# Derived from the Node base type.
class TimeNode(Node, CGTreeNode):
	
	# Description string
	'''Time node'''
	# Optional identifier string. If not explicitly defined, the python class name is used.
	bl_idname = 'TimeNodeType'
	# Label for nice name display
	bl_label = 'Time'
	# Icon identifier
	bl_icon = 'TIME'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Start")
		self.inputs.new('NodeSocketFloat', "Stop")
		self.inputs.new('NodeSocketFloat', "Scale")
		self.inputs.new('NodeSocketBool', "Enabled")
		self.inputs.new('NodeSocketBool', "Loop")
		self.inputs.new('NodeSocketBool', "Reflect")

		self.inputs["Stop"].default_value = -1
		self.inputs["Scale"].default_value = 1
		self.inputs["Enabled"].default_value = True
		
		self.outputs.new('NodeSocketFloat', "Time")
		
	#def draw_buttons(self, context, layout):
		#layout.prop(self, "startTime")
		#layout.prop(self, "stopTime")
	
	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
class VectorNode(Node, CGTreeNode):
	bl_idname = 'VectorNodeType'
	# Label for nice name display
	bl_label = 'Vector'
	# Icon identifier
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "X")
		self.inputs.new('NodeSocketFloat', "Y")
		self.inputs.new('NodeSocketFloat', "Z")
		
		self.outputs.new('NodeSocketVector', "Vector")
	
	def draw_buttons(self, context, layout):
		pass
		
	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
	def update(self):
		print("Updating node: ", self.name)
		render()


class ScaleValueNode(Node, CGTreeNode):
	bl_idname = 'ScaleValueNodeType'
	# Label for nice name display
	bl_label = 'ScaleValue'
	# Icon identifier
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Factor")
		self.inputs.new('NodeSocketFloat', "Value")

		self.inputs["Factor"].default_value = 1.0
		
		self.outputs.new('NodeSocketFloat', "Value")
	
	def draw_buttons(self, context, layout):
		pass
		
	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
	def update(self):
		print("Updating node: ", self.name)
		render()


class SineNode(Node, CGTreeNode):
	bl_idname = 'SineNodeType'
	# Label for nice name display
	bl_label = 'Sine'
	# Icon identifier
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Value")
		
		self.outputs.new('NodeSocketFloat', "Value")
	
	def draw_buttons(self, context, layout):
		pass
		
	def free(self):
		print("Removing node ", self, ", Goodbye!")
		
	def update(self):
		print("Updating node: ", self.name)
		render()


### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class MyNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CGTreeType'

# all categories in a list
node_categories = [
	# identifier, label, items list
	MyNodeCategory("TRANSFORMNODES", "Transform Nodes", items=[
		# our basic node
		NodeItem("TransformNodeType"),
		NodeItem("TimeNodeType"),
		NodeItem("VectorNodeType"),
		NodeItem("ScaleValueNodeType"),
		NodeItem("SineNodeType"),
		]),
	]

def register():
	bpy.utils.register_module(__name__)
	try:
		nodeitems_utils.register_node_categories("CG_NODES", node_categories)
	except:
		pass

def unregister():
	nodeitems_utils.unregister_node_categories("CG_NODES")
	bpy.utils.unregister_module(__name__)

# Generating node sources
def buildNodeTrees():
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure package dir exists
	nodes_path = 'Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/") + "/node"
	if not os.path.exists(nodes_path):
		os.makedirs(nodes_path)
	
	# Export node scripts
	for node_group in bpy.data.node_groups:
		if node_group.bl_idname == 'CGTreeType': # Build only game trees
			node_group.use_fake_user = True # Keep fake references for now
			buildNodeTree(node_group)

def buildNodeTree(node_group):
	rn = getRootNode(node_group)

	path = 'Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/") + "/node/"

	node_group_name = node_group.name.replace('.', '_')

	with open(path + node_group_name + '.hx', 'w') as f:
		f.write('package ' + bpy.data.worlds[0].CGProjectPackage + '.node;\n\n')
		f.write('import armory.node.*;\n\n')
		f.write('class ' + node_group_name + ' extends armory.trait.internal.NodeExecutor {\n\n')
		f.write('\tpublic function new() { super(); requestAdd(add); }\n\n')
		f.write('\tfunction add() {\n')
		# Make sure root node exists
		if rn != None:
			name = '_' + rn.name.replace(".", "_").replace("@", "")
			buildNode(node_group, rn, f, [])
			f.write('\n\t\tstart(' + name + ');\n')
		f.write('\t}\n')
		f.write('}\n')

def buildNode(node_group, node, f, created_nodes):
	# Get node name
	name = '_' + node.name.replace(".", "_").replace("@", "")

	# Check if node already exists
	for n in created_nodes:
		if n == name:
			return name

	# Create node
	type = node.name.split(".")[0].replace("@", "") + "Node"
	f.write('\t\tvar ' + name + ' = new ' + type + '();\n')
	created_nodes.append(name)
	
	# Variables
	if type == "TransformNode":
		f.write('\t\t' + name + '.transform = node.transform;\n')
	
	# Create inputs
	for inp in node.inputs:
		# Is linked - find node
		inpname = ''
		if inp.is_linked:
			n = findNodeByLink(node_group, node, inp)
			inpname = buildNode(node_group, n, f, created_nodes)
		# Not linked - create node with default values
		else:
			inpname = buildDefaultNode(inp)
		
		# Add input
		f.write('\t\t' + name + '.inputs.push(' + inpname + ');\n')
		
	return name
			
def findNodeByLink(node_group, to_node, inp):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == inp:
			return link.from_node
	
def getRootNode(node_group):
	for n in node_group.nodes:
		if n.outputs[0].is_linked == False:
			return n

def buildDefaultNode(inp):
	inpname = ''
	if inp.type == "VECTOR":
		inpname = 'VectorNode.create(' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ", " + str(inp.default_value[2]) + ')'
	elif inp.type == "VALUE":
		inpname = 'FloatNode.create(' + str(inp.default_value) + ')'
	elif inp.type == 'BOOLEAN':
		inpname = 'BoolNode.create(' + str(inp.default_value).lower() + ')'
		
	return inpname
