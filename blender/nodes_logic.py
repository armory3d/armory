import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
	
class CGTree(NodeTree):
	'''Logic nodes'''
	bl_idname = 'ArmLogicTreeType'
	bl_label = 'Logic Node Tree'
	bl_icon = 'GAME'

	#def update(self):
		#print("runing tree")

class ArmLogicTreeNode:
	@classmethod
	def poll(cls, ntree):
		return ntree.bl_idname == 'ArmLogicTreeType'


class TransformNode(Node, ArmLogicTreeNode):
	'''Transform node'''
	bl_idname = 'TransformNodeType'
	bl_label = 'Transform'
	bl_icon = 'SOUND'

	def init(self, context):
		self.inputs.new('NodeSocketVector', "Position")
		self.inputs.new('NodeSocketVector', "Rotation")
		self.inputs.new('NodeSocketVector', "Scale")
		self.inputs[-1].default_value = [1.0, 1.0, 1.0]

		self.outputs.new('NodeSocketString', "Transform")

	# Copy function to initialize a copied node from an existing one.
	# def copy(self, node):
		# print("Copying from node ", node)

	# Free function to clean up on removal.
	# def free(self):
		# print("Removing node ", self, ", Goodbye!")

class TimeNode(Node, ArmLogicTreeNode):
	'''Time node'''
	bl_idname = 'TimeNodeType'
	bl_label = 'Time'
	bl_icon = 'TIME'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Start")
		self.inputs.new('NodeSocketFloat', "Stop")
		self.inputs[-1].default_value = -1
		self.inputs.new('NodeSocketBool', "Enabled")
		self.inputs[-1].default_value = True
		self.inputs.new('NodeSocketBool', "Loop")
		self.inputs.new('NodeSocketBool', "Reflect")
		
		self.outputs.new('NodeSocketFloat', "Time")
		
class VectorNode(Node, ArmLogicTreeNode):
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

class ScaleValueNode(Node, ArmLogicTreeNode):
	bl_idname = 'ScaleValueNodeType'
	bl_label = 'ScaleValue'
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Factor")
		self.inputs[-1].default_value = 1.0
		self.inputs.new('NodeSocketFloat', "Value")
		
		self.outputs.new('NodeSocketFloat', "Value")

class SineNode(Node, ArmLogicTreeNode):
	bl_idname = 'SineNodeType'
	bl_label = 'Sine'
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Value")
		
		self.outputs.new('NodeSocketFloat', "Value")

class ThisNode(Node, ArmLogicTreeNode):
	bl_idname = 'ThisNodeType'
	bl_label = 'This'
	bl_icon = 'GAME'
	
	def init(self, context):
		self.outputs.new('NodeSocketShader', "Target")

class PickerNode(Node, ArmLogicTreeNode):
	bl_idname = 'PickerNodeType'
	bl_label = 'Picker'
	bl_icon = 'GAME'
	property0 = StringProperty(name = "Object", default="")

	def init(self, context):
		self.outputs.new('NodeSocketShader', "Target")

	def draw_buttons(self, context, layout):
		layout.prop_search(self, "property0", context.scene, "objects", text = "")

class SetTransformNode(Node, ArmLogicTreeNode):
	bl_idname = 'SetTransformNodeType'
	bl_label = 'Set Transform'
	bl_icon = 'GAME'

	def init(self, context):
		self.inputs.new('NodeSocketShader', "Target")
		self.inputs.new('NodeSocketShader', "Transform")

class SetVisibleNode(Node, ArmLogicTreeNode):
	bl_idname = 'SetVisibleNodeType'
	bl_label = 'Set Visible'
	bl_icon = 'GAME'

	def init(self, context):
		self.inputs.new('NodeSocketShader', "Target")
		self.inputs.new('NodeSocketShader', "Bool")

class GreaterThanNode(Node, ArmLogicTreeNode):
	bl_idname = 'GreaterThanNodeType'
	bl_label = 'Greater Than'
	bl_icon = 'GAME'

	def init(self, context):
		self.inputs.new('NodeSocketFloat', "Value 1")
		self.inputs.new('NodeSocketFloat', "Value 2")
		self.outputs.new('NodeSocketBool', "Bool")


### Node Categories ###
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class ObjectNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'ArmLogicTreeType'

class TypeNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'ArmLogicTreeType'

class MathNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'ArmLogicTreeType'

class LogicNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'ArmLogicTreeType'

node_categories = [
	ObjectNodeCategory("LOGICTARGETNODES", "Target", items=[
		NodeItem("ThisNodeType"),
		NodeItem("PickerNodeType"),
		NodeItem("SetTransformNodeType"),
		NodeItem("SetVisibleNodeType"),
	]),
	TypeNodeCategory("LOGICTYPENODES", "Type", items=[
		NodeItem("TransformNodeType"),
		NodeItem("VectorNodeType"),
	]),
	MathNodeCategory("LOGICMATHNODES", "Math", items=[
		NodeItem("TimeNodeType"),
		NodeItem("ScaleValueNodeType"),
		NodeItem("SineNodeType"),
	]),
	LogicNodeCategory("LOGICLOGICNODES", "Logic", items=[
		NodeItem("GreaterThanNodeType"),
	]),
]

def register():
	bpy.utils.register_module(__name__)
	try:
		nodeitems_utils.register_node_categories("ARM_LOGIC_NODES", node_categories)
	except:
		pass

def unregister():
	nodeitems_utils.unregister_node_categories("ARM_LOGIC_NODES")
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
		if node_group.bl_idname == 'ArmLogicTreeType': # Build only game trees
			node_group.use_fake_user = True # Keep fake references for now
			buildNodeTree(node_group)

def buildNodeTree(node_group):
	path = 'Sources/' + bpy.data.worlds[0].CGProjectPackage.replace('.', '/') + '/node/'
	node_group_name = node_group.name.replace('.', '_').replace(' ', '')

	with open(path + node_group_name + '.hx', 'w') as f:
		f.write('package ' + bpy.data.worlds[0].CGProjectPackage + '.node;\n\n')
		f.write('import armory.node.*;\n\n')
		f.write('class ' + node_group_name + ' extends armory.trait.internal.NodeExecutor {\n\n')
		f.write('\tpublic function new() { super(); notifyOnAdd(add); }\n\n')
		f.write('\tfunction add() {\n')
		# Make sure root node exists
		roots = getRootNodes(node_group)
		created_nodes = []
		for rn in roots:
			name = '_' + rn.name.replace('.', '_').replace(' ', '')
			buildNode(node_group, rn, f, created_nodes)
			f.write('\n\t\tstart(' + name + ');\n\n')
		f.write('\t}\n')
		f.write('}\n')

def buildNode(node_group, node, f, created_nodes):
	# Get node name
	name = '_' + node.name.replace('.', '_').replace(' ', '')

	# Check if node already exists
	for n in created_nodes:
		if n == name:
			return name

	# Create node
	type = node.name.split(".")[0].replace(' ', '') + "Node"
	f.write('\t\tvar ' + name + ' = new ' + type + '();\n')
	created_nodes.append(name)
	
	# Properties
	if hasattr(node, "property0"):
		f.write('\t\t' + name + '.property0 = "' + node.property0 + '";\n')
	if hasattr(node, "property1"):
		f.write('\t\t' + name + '.property1 = "' + node.property1 + '";\n')
	if hasattr(node, "property2"):
		f.write('\t\t' + name + '.property2 = "' + node.property2 + '";\n')
	if hasattr(node, "property3"):
		f.write('\t\t' + name + '.property3 = "' + node.property3 + '";\n')
	if hasattr(node, "property4"):
		f.write('\t\t' + name + '.property4 = "' + node.property4 + '";\n')
	
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
			if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
				return findNodeByLink(node_group, link.from_node, link.from_node.inputs[0])
			return link.from_node
	
def getRootNodes(node_group):
	roots = []
	for n in node_group.nodes:
		if len(n.outputs) == 0: # Assume node with no outputs as roots
			roots.append(n)
	return roots

def buildDefaultNode(inp):
	inpname = ''
	if inp.type == "VECTOR":
		inpname = 'VectorNode.create(' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ", " + str(inp.default_value[2]) + ')'
	elif inp.type == "VALUE":
		inpname = 'FloatNode.create(' + str(inp.default_value) + ')'
	elif inp.type == 'BOOLEAN':
		inpname = 'BoolNode.create(' + str(inp.default_value).lower() + ')'
		
	return inpname
