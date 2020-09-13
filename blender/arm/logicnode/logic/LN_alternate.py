from arm.logicnode.arm_nodes import *


class AlternateNode(ArmLogicTreeNode):
    """Alternate node"""
    bl_idname = 'LNAlternateNode'
    bl_label = 'Alternate'
    arm_version = 1

    def init(self, context):
        super(AlternateNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', '0')
        self.add_output('ArmNodeSocketAction', '1')


add_node(AlternateNode, category=PKG_AS_CATEGORY, section='flow')
