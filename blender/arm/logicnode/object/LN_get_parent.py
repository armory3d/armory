from arm.logicnode.arm_nodes import *

class GetParentNode(ArmLogicTreeNode):
    """Get parent node"""
    bl_idname = 'LNGetParentNode'
    bl_label = 'Get Parent'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GetParentNode, category=PKG_AS_CATEGORY, section='relations')
