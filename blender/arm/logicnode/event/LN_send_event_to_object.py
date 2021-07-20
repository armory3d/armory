from arm.logicnode.arm_nodes import *

class SendEventNode(ArmLogicTreeNode):
    """Sends a event to the given object.

    @seeNode Send Event
    @seeNode On Event

    @input Event: the identifier of the event
    @input Object: the receiving object"""
    bl_idname = 'LNSendEventNode'
    bl_label = 'Send Event to Object'
    arm_section = 'custom'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Event')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')
