from arm.logicnode.arm_nodes import *

class GetGroupNode(ArmLogicTreeNode):
    """Get group node"""
    bl_idname = 'LNGetGroupNode'
    bl_label = 'Get Collection'

    def init(self, context):
        self.add_input('NodeSocketString', 'Name')
        self.add_output('ArmNodeSocketArray', 'Array')

add_node(GetGroupNode, category=PKG_AS_CATEGORY, section='collection')
