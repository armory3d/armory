from arm.logicnode.arm_nodes import *

class GoToLocationNode(ArmLogicTreeNode):
    """Navigate to location node"""
    bl_idname = 'LNGoToLocationNode'
    bl_label = 'Go To Location'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Location')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(GoToLocationNode, category=PKG_AS_CATEGORY)
