from arm.logicnode.arm_nodes import *

class LenstextureSetNode(ArmLogicTreeNode):
    """Set Lenstexture Effect"""
    bl_idname = 'LNLenstextureSetNode'
    bl_label = 'Set Lenstexture'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Center Min Clip', default_value=0.1)
        self.add_input('NodeSocketFloat', 'Center Max Clip', default_value=0.5)
        self.add_input('NodeSocketFloat', 'Luminance Min', default_value=0.10)
        self.add_input('NodeSocketFloat', 'Luminance Max', default_value=2.50)
        self.add_input('NodeSocketFloat', 'Brightness Exponent', default_value=2.0)

        self.add_output('ArmNodeSocketAction', 'Out')

add_node(LenstextureSetNode, category=PKG_AS_CATEGORY)
