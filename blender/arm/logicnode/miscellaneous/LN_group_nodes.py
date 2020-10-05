from arm.logicnode.arm_nodes import *

class GroupOutputNode(ArmLogicTreeNode):
    """Sets the connected chain of nodes as a group of nodes."""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Group Nodes'
    arm_version = 1

    def init(self, context):
        super(GroupOutputNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')

add_node(GroupOutputNode, category=PKG_AS_CATEGORY, section='group')
