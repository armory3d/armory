import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LenstextureGetNode(Node, ArmLogicTreeNode):
    '''Get Tonemapper Effect'''
    bl_idname = 'LNLenstextureGetNode'
    bl_label = 'Get Lenstexture'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Center Min Clip')
        self.outputs.new('NodeSocketFloat', 'Center Max Clip')
        self.outputs.new('NodeSocketFloat', 'Luminance Min')
        self.outputs.new('NodeSocketFloat', 'Luminance Max')
        self.outputs.new('NodeSocketFloat', 'Brightness Exponent')

add_node(LenstextureGetNode, category='Postprocess')
