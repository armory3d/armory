from arm.logicnode.arm_nodes import *

class DrawLineNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawLineNode'
    bl_label = 'Draw Line'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Desativated', default_value = True)
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength')
        self.add_input('ArmIntSocket', 'X1')
        self.add_input('ArmIntSocket', 'Y1')
        self.add_input('ArmIntSocket', 'X2')
        self.add_input('ArmIntSocket', 'Y2')

        self.add_output('ArmNodeSocketAction', 'Out')
        