from arm.logicnode.arm_nodes import *

class GetTilesheetStateNode(ArmLogicTreeNode):
    """Returns the information about the current tilesheet of the given object."""
    bl_idname = 'LNGetTilesheetStateNode'
    bl_label = 'Get Tilesheet State'
    arm_version = 1
    arm_section = 'tilesheet'

    def init(self, context):
        super(GetTilesheetStateNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('NodeSocketString', 'Name')
        self.add_output('NodeSocketInt', 'Frame')
        self.add_output('NodeSocketBool', 'Is Paused')
