from arm.logicnode.arm_nodes import *


class IsNoneNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in value is
    `null` (no value).

    @seeNode Is Not None"""
    bl_idname = 'LNIsNoneNode'
    bl_label = 'Is None'
    arm_version = 1

    def init(self, context):
        super(IsNoneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(IsNoneNode, category=PKG_AS_CATEGORY)
