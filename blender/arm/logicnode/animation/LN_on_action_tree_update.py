from arm.logicnode.arm_nodes import *

class OnAnimationTreeUpdateNode(ArmLogicTreeNode):
    """Execute output when animation tree is updated"""
    bl_idname = 'LNOnAnimationTreeUpdateNode'
    bl_label = 'On Animation Tree Update'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAnimTree', 'Action Tree')
        self.add_output('ArmNodeSocketAnimTree', 'Action Tree')
        self.add_output('ArmNodeSocketAction', 'Out')