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

    def draw_label(self) -> str:
        if self.inputs[1].is_linked:
            return self.bl_label
        return f'{self.bl_label}: {self.inputs[1].get_default_value()}'
