import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVelocityNode(Node, ArmLogicTreeNode):
    '''Set velocity node'''
    bl_idname = 'LNSetVelocityNode'
    bl_label = 'Set Velocity'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Linear')
        self.inputs.new('NodeSocketVector', 'Linear Factor')
        self.inputs[-1].default_value = [1.0, 1.0, 1.0]
        self.inputs.new('NodeSocketVector', 'Angular')
        self.inputs.new('NodeSocketVector', 'Angular Factor')
        self.inputs[-1].default_value = [1.0, 1.0, 1.0]
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetVelocityNode, category='Physics')
