from arm.logicnode.arm_nodes import *

class ReplaceObjectNode(ArmLogicTreeNode):
    """Replace location and rotation between two objects"""
    bl_idname = 'LNReplaceObjectNode'
    bl_label = 'Replace Object'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Base')
        self.add_input('ArmNodeSocketObject', 'Replace')
        self.add_input('ArmBoolSocket', 'Invert')
        self.add_input('ArmBoolSocket', 'Scale')
        self.add_output('ArmNodeSocketAction', 'Out')
