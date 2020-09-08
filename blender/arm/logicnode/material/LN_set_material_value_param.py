import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialValueParamNode(Node, ArmLogicTreeNode):
    '''Set material value param node'''
    bl_idname = 'LNSetMaterialValueParamNode'
    bl_label = 'Set Material Value Param'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Material')
        self.inputs.new('NodeSocketString', 'Node')
        self.inputs.new('NodeSocketFloat', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMaterialValueParamNode, category=MODULE_AS_CATEGORY, section='params')
