import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RotateObjectNode(Node, ArmLogicTreeNode):
    '''Rotate object node'''
    bl_idname = 'LNRotateObjectNode'
    bl_label = 'Rotate Object'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RotateObjectNode, category='Action')
