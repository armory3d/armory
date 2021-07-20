from arm.logicnode.arm_nodes import *

class GroupOutputNode(ArmLogicTreeNode):
    """Sets the connected chain of nodes as a group of nodes."""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Group Nodes'
    arm_section = 'group'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
