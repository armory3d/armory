import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SendObjectEventNode(Node, ArmLogicTreeNode):
    '''Send object event node'''
    bl_idname = 'LNSendObjectEventNode'
    bl_label = 'Send Object Event'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Event')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SendObjectEventNode, category='Action')
