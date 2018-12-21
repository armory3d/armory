import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetGravityEnabledNode(Node, ArmLogicTreeNode):
    '''Node to enable or disable gravity on a specific object.'''
    bl_idname = 'LNSetGravityEnabledNode'
    bl_label = 'Set Gravity Enabled'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Enabled')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetGravityEnabledNode, category='Physics')
