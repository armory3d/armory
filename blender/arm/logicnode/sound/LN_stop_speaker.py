from arm.logicnode.arm_nodes import *

class StopSpeakerNode(ArmLogicTreeNode):
    """Stops playback of the given speaker object. The playback position will be
    reset to the start.

    @seeNode Pause Speaker
    @seeNode Play Speaker
    """
    bl_idname = 'LNStopSoundNode'
    bl_label = 'Stop Speaker'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')

        self.add_output('ArmNodeSocketAction', 'Out')
