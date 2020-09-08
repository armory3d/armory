import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LenstextureGetNode(ArmLogicTreeNode):
    """Get Tonemapper Effect"""
    bl_idname = 'LNLenstextureGetNode'
    bl_label = 'Get Lenstexture'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Center Min Clip')
        self.add_output('NodeSocketFloat', 'Center Max Clip')
        self.add_output('NodeSocketFloat', 'Luminance Min')
        self.add_output('NodeSocketFloat', 'Luminance Max')
        self.add_output('NodeSocketFloat', 'Brightness Exponent')

add_node(LenstextureGetNode, category=MODULE_AS_CATEGORY)
