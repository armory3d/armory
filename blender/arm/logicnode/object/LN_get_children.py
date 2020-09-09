from arm.logicnode.arm_nodes import *

class GetChildrenNode(ArmLogicTreeNode):
    """Get children node"""
    bl_idname = 'LNGetChildrenNode'
    bl_label = 'Get Children'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketArray', 'Array')

add_node(GetChildrenNode, category=PKG_AS_CATEGORY, section='relations')
