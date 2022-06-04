from arm.logicnode.arm_nodes import *

class DrawStringNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawStringNode'
    bl_label = 'Draw String'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Deactivated', default_value = True)
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Font File')
        self.add_input('ArmIntSocket', 'Font Size')
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')

        self.add_output('ArmNodeSocketAction', 'Out')
        