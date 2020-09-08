import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsNotNoneNode(ArmLogicTreeNode):
    '''Is not none node'''
    bl_idname = 'LNIsNotNoneNode'
    bl_label = 'Is Not None'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(IsNotNoneNode, category=MODULE_AS_CATEGORY)
