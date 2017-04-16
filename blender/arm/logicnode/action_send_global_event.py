import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SendGlobalEventNode(Node, ArmLogicTreeNode):
    '''Send global event node'''
    bl_idname = 'LNSendGlobalEventNode'
    bl_label = 'Send Global Event'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Event')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SendGlobalEventNode, category='Action')
