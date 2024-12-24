from arm.logicnode.arm_nodes import *


@deprecated('Set Tilesheet Paused')
class PauseTilesheetNode(ArmLogicTreeNode):
    """Pauses the given tilesheet action."""
    bl_idname = 'LNPauseTilesheetNode'
    bl_label = 'Pause Tilesheet'
    bl_description = "Please use the \"Set Tilesheet Paused\" node instead"
    arm_category = 'Animation'
    arm_section = 'tilesheet'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')
