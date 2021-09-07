from arm.logicnode.arm_nodes import *

class PlayAnimationTreeNode(ArmLogicTreeNode):
    """Plays a given animation tree."""
    bl_idname = 'LNPlayAnimationTreeNode'
    bl_label = 'Play Animation Tree'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Action Tree')

        self.add_output('ArmNodeSocketAction', 'Out')