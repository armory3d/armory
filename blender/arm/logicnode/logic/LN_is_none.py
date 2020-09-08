from arm.logicnode.arm_nodes import *


class IsNoneNode(ArmLogicTreeNode):
    """Is none node"""
    bl_idname = 'LNIsNoneNode'
    bl_label = 'Is None'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(IsNoneNode, category=MODULE_AS_CATEGORY)
