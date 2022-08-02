from arm.logicnode.arm_nodes import *

class PlaySpeakerNode(ArmLogicTreeNode):
    """Starts the playback of the given speaker object. If the playback was
    paused, it is resumed from the paused position.

    @seeNode Pause Speaker
    @seeNode Play Speaker
    """
    bl_idname = 'LNPlaySoundNode'
    bl_label = 'Play Speaker'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')

        self.add_output('ArmNodeSocketAction', 'Out')
