import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetLightColorNode(Node, ArmLogicTreeNode):
    '''Set light color node'''
    bl_idname = 'LNSetLightColorNode'
    bl_label = 'Set Light Color'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketColor', 'Color')
        self.inputs[-1].default_value = [1.0, 1.0, 1.0, 1.0]
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetLightColorNode, category='Action')
