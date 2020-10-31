from arm.logicnode.arm_nodes import *

class IsNotNoneNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in value is
    not `null`.

    @seeNode Is None"""
    bl_idname = 'LNIsNotNoneNode'
    bl_label = 'Is Not Null'
    arm_version = 1

    def init(self, context):
        super(IsNotNoneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
