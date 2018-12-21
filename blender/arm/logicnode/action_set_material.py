import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialNode(Node, ArmLogicTreeNode):
    '''Set material node'''
    bl_idname = 'LNSetMaterialNode'
    bl_label = 'Set Material'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Material')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMaterialNode, category='Action')
