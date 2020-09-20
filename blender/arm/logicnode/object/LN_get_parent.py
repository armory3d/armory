from arm.logicnode.arm_nodes import *

class GetParentNode(ArmLogicTreeNode):
    """Get parent node"""
    bl_idname = 'LNGetParentNode'
    bl_label = 'Get Parent'
    arm_version = 1

    def init(self, context):
        super(GetParentNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Child')
        self.add_output('ArmNodeSocketObject', 'Parent')

add_node(GetParentNode, category=PKG_AS_CATEGORY, section='relations')
