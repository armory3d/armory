from arm.logicnode.arm_nodes import *

class SetTilesheetPausedNode(ArmLogicTreeNode):
    """Sets the tilesheet paused state of the given object."""
    bl_idname = 'LNSetTilesheetPausedNode'
    bl_label = 'Set Tilesheet Paused'
    arm_section = 'tilesheet'
    arm_version = 1

    def init(self, context):
        super(SetTilesheetPausedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Paused')
        self.add_output('ArmNodeSocketAction', 'Out')
