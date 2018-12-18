import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetTransformNode(Node, ArmLogicTreeNode):
    '''Set transform node'''
    bl_idname = 'LNSetTransformNode'
    bl_label = 'Set Transform'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetTransformNode, category='Action')
