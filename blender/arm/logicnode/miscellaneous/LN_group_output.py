from arm.logicnode.arm_nodes import *

class GroupOutputNode(ArmLogicTreeNode):
    """Group output node"""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Node Group Output'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

add_node(GroupOutputNode, category=MODULE_AS_CATEGORY, section='group')
