from arm.logicnode.arm_nodes import *

class DrawImageSequenceNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawImageSequenceNode'
    bl_label = 'Draw Image Sequence'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Deactivated', default_value = True)
        self.add_input('ArmStringSocket', 'Image File Prefix')
        self.add_input('ArmStringSocket', 'Image File Extension')
        self.add_input('ArmIntSocket', 'From')
        self.add_input('ArmIntSocket', 'To')
        self.add_input('ArmIntSocket', 'Rate')
        self.add_input('ArmBoolSocket', 'Loop', default_value = True)
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmIntSocket', 'X')
        self.add_input('ArmIntSocket', 'Y')
        self.add_input('ArmIntSocket', 'W')
        self.add_input('ArmIntSocket', 'H')

        self.add_output('ArmNodeSocketAction', 'Out')
        