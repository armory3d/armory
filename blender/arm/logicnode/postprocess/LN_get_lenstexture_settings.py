from arm.logicnode.arm_nodes import *

class LenstextureGetNode(ArmLogicTreeNode):
    """Use to get the lens texture settings."""
    bl_idname = 'LNLenstextureGetNode'
    bl_label = 'Get Lenstexture Settings'
    arm_version = 1

    def init(self, context):
        super(LenstextureGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Center Min Clip')
        self.add_output('NodeSocketFloat', 'Center Max Clip')
        self.add_output('NodeSocketFloat', 'Luminance Min')
        self.add_output('NodeSocketFloat', 'Luminance Max')
        self.add_output('NodeSocketFloat', 'Brightness Exponent')

add_node(LenstextureGetNode, category=PKG_AS_CATEGORY)
