import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LenstextureSetNode(ArmLogicTreeNode):
    '''Set Lenstexture Effect'''
    bl_idname = 'LNLenstextureSetNode'
    bl_label = 'Set Lenstexture'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'Center Min Clip')
        self.inputs[-1].default_value = 0.1
        self.inputs.new('NodeSocketFloat', 'Center Max Clip')
        self.inputs[-1].default_value = 0.5
        self.inputs.new('NodeSocketFloat', 'Luminance Min')
        self.inputs[-1].default_value = 0.10
        self.inputs.new('NodeSocketFloat', 'Luminance Max')
        self.inputs[-1].default_value = 2.50
        self.inputs.new('NodeSocketFloat', 'Brightness Exponent')
        self.inputs[-1].default_value = 2.0

        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(LenstextureSetNode, category=MODULE_AS_CATEGORY)
