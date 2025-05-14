from arm.logicnode.arm_nodes import *


class NetworkHostGetIpNode(ArmLogicTreeNode):
    """Return an IP from the ID of a connection"""
    bl_idname = 'LNNetworkHostGetIpNode'
    bl_label = 'Host Get IP'
    arm_version = 1


    property0: HaxeBoolProperty(
        'property0',
        name="Secure",
        description="Secure host connection",
        default=False,
    )


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Connection')
        self.add_input('ArmStringSocket', 'ID')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'IP')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
