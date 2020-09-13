from arm.logicnode.arm_nodes import *

class LenstextureGetNode(ArmLogicTreeNode):
    """Get Tonemapper Effect"""
    bl_idname = 'LNLenstextureGetNode'
    bl_label = 'Get Lenstexture'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Center Min Clip')
        self.add_output('NodeSocketFloat', 'Center Max Clip')
        self.add_output('NodeSocketFloat', 'Luminance Min')
        self.add_output('NodeSocketFloat', 'Luminance Max')
        self.add_output('NodeSocketFloat', 'Brightness Exponent')

add_node(LenstextureGetNode, category=PKG_AS_CATEGORY)
