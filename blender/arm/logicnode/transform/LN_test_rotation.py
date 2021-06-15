from arm.logicnode.arm_nodes import *

class TestRotationNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNTestRotationNode'
    bl_label = 'TEST NODE DO NOT USE'
    arm_section = 'quaternions'
    arm_version = 1

    def init(self, context):
        super(TestRotationNode, self).init(context)
        self.add_input('ArmNodeSocketRotation', 'taste')
