from arm.logicnode.arm_nodes import *

class SendGlobalEventNode(ArmLogicTreeNode):
    """Send global event node"""
    bl_idname = 'LNSendGlobalEventNode'
    bl_label = 'Send Global Event'
    arm_version = 1

    def init(self, context):
        super(SendGlobalEventNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Event')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SendGlobalEventNode, category=PKG_AS_CATEGORY, section='custom')
