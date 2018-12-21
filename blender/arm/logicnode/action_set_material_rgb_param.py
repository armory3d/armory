import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialRgbParamNode(Node, ArmLogicTreeNode):
    '''Set material rgb param node'''
    bl_idname = 'LNSetMaterialRgbParamNode'
    bl_label = 'Set Material RGB Param'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Material')
        self.inputs.new('NodeSocketString', 'Node')
        self.inputs.new('NodeSocketColor', 'Color')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMaterialRgbParamNode, category='Action')
