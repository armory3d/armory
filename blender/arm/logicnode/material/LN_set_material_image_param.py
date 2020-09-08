import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialImageParamNode(ArmLogicTreeNode):
    '''Set material image param node'''
    bl_idname = 'LNSetMaterialImageParamNode'
    bl_label = 'Set Material Image Param'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Material')
        self.inputs.new('NodeSocketString', 'Node')
        self.inputs.new('NodeSocketString', 'Image')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMaterialImageParamNode, category=MODULE_AS_CATEGORY, section='params')
