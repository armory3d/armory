from arm.logicnode.arm_nodes import *

class DrawCircleNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawCircleNode'
    bl_label = 'Draw Circle'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Desativated', default_value = True)
        self.add_input('ArmBoolSocket', 'Filled', default_value = False)
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength')
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')
        self.add_input('ArmIntSocket', 'Radio')
        self.add_input('ArmIntSocket', 'Segments')

        self.add_output('ArmNodeSocketAction', 'Out')
        