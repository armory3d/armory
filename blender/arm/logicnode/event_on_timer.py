import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnTimerNode(Node, ArmLogicTreeNode):
    '''On timer node'''
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Duration')
        self.inputs.new('NodeSocketBool', 'Repeat')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(OnTimerNode, category='Event')
