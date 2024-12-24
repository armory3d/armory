from arm.logicnode.arm_nodes import *

class LenstextureGetNode(ArmLogicTreeNode):
    """Returns the lens texture settings."""
    bl_idname = 'LNLenstextureGetNode'
    bl_label = 'Get Lenstexture Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Center Min Clip')
        self.add_output('ArmFloatSocket', 'Center Max Clip')
        self.add_output('ArmFloatSocket', 'Luminance Min')
        self.add_output('ArmFloatSocket', 'Luminance Max')
        self.add_output('ArmFloatSocket', 'Brightness Exponent')
