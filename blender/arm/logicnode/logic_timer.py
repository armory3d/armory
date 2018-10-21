import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TimerNode(Node, ArmLogicTreeNode):
	'''Timer node'''
	bl_idname = 'LNTimerNode'
	bl_label = 'Timer'
	bl_icon = 'CURVE_PATH'
	
	def init(self, context):
		self.inputs.new('ArmNodeSocketAction', 'In')
		self.inputs.new('NodeSocketFloat', 'Duration')
		self.inputs.new('NodeSocketInt', 'Repeat')
		self.inputs.new('NodeSocketBool', 'Pause')

		self.outputs.new('ArmNodeSocketAction', 'Out')
		self.outputs.new('NodeSocketBool', 'Running')
		self.outputs.new('NodeSocketInt', 'secondsPassed')
		self.outputs.new('NodeSocketInt', 'secondsLeft')
		self.outputs.new('NodeSocketFloat', 'Normalized')
	
		self.inputs['Repeat'].default_value = 1
		
add_node(TimerNode, category='Logic')
