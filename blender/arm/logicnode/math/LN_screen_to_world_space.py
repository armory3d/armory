from arm.logicnode.arm_nodes import *

class ScreenToWorldSpaceNode(ArmLogicTreeNode):
    """Screen to world space node"""
    bl_idname = 'LNScreenToWorldSpaceNode'
    bl_label = 'Screen To World Space'
    arm_version = 1

    def init(self, context):
        super(ScreenToWorldSpaceNode, self).init(context)
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketVector', 'Vector')

add_node(ScreenToWorldSpaceNode, category=PKG_AS_CATEGORY, section='matrix')
