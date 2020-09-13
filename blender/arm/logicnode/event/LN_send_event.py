from arm.logicnode.arm_nodes import *

class SendEventNode(ArmLogicTreeNode):
    """Send event node"""
    bl_idname = 'LNSendEventNode'
    bl_label = 'Send Event'
    arm_version = 1

    def init(self, context):
        super(SendEventNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Event')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SendEventNode, category=PKG_AS_CATEGORY, section='custom')
