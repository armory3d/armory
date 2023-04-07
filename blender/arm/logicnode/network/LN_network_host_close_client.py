from arm.logicnode.arm_nodes import *


class NetworkHostCloseClientNode(ArmLogicTreeNode):
    """Close a client from a host connection by ID"""
    bl_idname = 'LNNetworkHostCloseClientNode'
    bl_label = 'Host Close Client'
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

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
