from arm.logicnode.arm_nodes import *

class RemoveInputMapKeyNode(ArmLogicTreeNode):
    """Remove input map key."""
    bl_idname = 'LNRemoveInputMapKeyNode'
    bl_label = 'Remove Input Map Key'
    arm_version = 1

    def init(self, context):
        super(RemoveInputMapKeyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Input Map')
        self.add_input('NodeSocketString', 'Key')

        self.add_output('ArmNodeSocketAction', 'Out')