import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetActivationStateNode (Node, ArmLogicTreeNode):
    '''Set Activation State Node'''
    bl_idname = 'LNSetActivationStateNode'
    bl_label = 'Set Activation State'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketInt', 'State')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetActivationStateNode, category='Physics')
