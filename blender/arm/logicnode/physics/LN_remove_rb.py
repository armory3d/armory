from arm.logicnode.arm_nodes import *

class RemovePhysicsNode (ArmLogicTreeNode):
    """Removes the rigid body from the given object."""
    bl_idname = 'LNRemovePhysicsNode'
    bl_label = 'Remove RB'
    arm_version = 1

    def init(self, context):
        super(RemovePhysicsNode, self).init(context)
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'RB')

        self.outputs.new('ArmNodeSocketAction', 'Out')
