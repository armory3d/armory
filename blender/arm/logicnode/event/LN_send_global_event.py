from arm.logicnode.arm_nodes import *

class SendGlobalEventNode(ArmLogicTreeNode):
    """Sends the given event to all objects in the scene.

    @seeNode Send Event to Object
    @seeNode On Event

    @input Event: the identifier of the event"""
    bl_idname = 'LNSendGlobalEventNode'
    bl_label = 'Send Global Event'
    arm_version = 1
    arm_section = 'custom'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Event')

        self.add_output('ArmNodeSocketAction', 'Out')
