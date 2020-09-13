from arm.logicnode.arm_nodes import *

class NotNode(ArmLogicTreeNode):
    """Not node"""
    bl_idname = 'LNNotNode'
    bl_label = 'Not'
    arm_version = 1

    def init(self, context):
        super(NotNode, self).init(context)
        self.add_input('NodeSocketBool', 'Value')
        self.add_output('NodeSocketBool', 'Value')

add_node(NotNode, category=PKG_AS_CATEGORY)
