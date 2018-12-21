import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ClearParentNode(Node, ArmLogicTreeNode):
    '''Clear parent node'''
    bl_idname = 'LNClearParentNode'
    bl_label = 'Clear Parent'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Keep Transform')
        self.inputs[-1].default_value = True
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ClearParentNode, category='Action')
