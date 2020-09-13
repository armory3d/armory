from arm.logicnode.arm_nodes import *

class GroupOutputNode(ArmLogicTreeNode):
    """Group output node"""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Node Group Output'
    arm_version = 1

    def init(self, context):
        super(GroupOutputNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')

add_node(GroupOutputNode, category=PKG_AS_CATEGORY, section='group')
