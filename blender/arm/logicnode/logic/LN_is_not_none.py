from arm.logicnode.arm_nodes import *

class IsNotNoneNode(ArmLogicTreeNode):
    """Is not none node"""
    bl_idname = 'LNIsNotNoneNode'
    bl_label = 'Is Not None'
    arm_version = 1

    def init(self, context):
        super(IsNotNoneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(IsNotNoneNode, category=PKG_AS_CATEGORY)
