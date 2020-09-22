from arm.logicnode.arm_nodes import *

class GetCursorLocationNode(ArmLogicTreeNode):
    """Get Cursor Location node"""
    bl_idname = 'LNGetCursorLocationNode'
    bl_label = 'Get Cursor Location'
    arm_version = 1

    def init(self, context):
        super(GetCursorLocationNode, self).init(context)
        self.add_output('NodeSocketInt', 'X')
        self.add_output('NodeSocketInt', 'Y')
        self.add_output('NodeSocketInt', 'Inverted X')
        self.add_output('NodeSocketInt', 'Inverted Y')

add_node(GetCursorLocationNode, category=PKG_AS_CATEGORY, section='mouse')
