from arm.logicnode.arm_nodes import *

class SetSoundSpeakerNode(ArmLogicTreeNode):
    """sets sound name of the given speaker object.

    @seeNode Play Speaker
    @seeNode Stop Speaker
    """
    bl_idname = 'LNSetSoundNode'
    bl_label = 'Set Sound Speaker'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_input('ArmStringSocket', 'Sound Name')

        self.add_output('ArmNodeSocketAction', 'Out')
