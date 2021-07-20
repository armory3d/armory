from arm.logicnode.arm_nodes import *

class LenstextureSetNode(ArmLogicTreeNode):
    """Set the lens texture settings."""
    bl_idname = 'LNLenstextureSetNode'
    bl_label = 'Set Lenstexture'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Center Min Clip', default_value=0.1)
        self.add_input('ArmFloatSocket', 'Center Max Clip', default_value=0.5)
        self.add_input('ArmFloatSocket', 'Luminance Min', default_value=0.10)
        self.add_input('ArmFloatSocket', 'Luminance Max', default_value=2.50)
        self.add_input('ArmFloatSocket', 'Brightness Exponent', default_value=2.0)

        self.add_output('ArmNodeSocketAction', 'Out')
