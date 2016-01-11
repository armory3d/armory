import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
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
	#	  This can be used to make additional tree types for groups and similar nodes (see below)
	#	  Only one base tree class is needed in the editor for selecting the general category
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
	#	  a purely internal Python method and unknown to the node system!
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
