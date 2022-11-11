from arm.logicnode.arm_nodes import *


class NetworkOpenConnectionNode(ArmLogicTreeNode):
    """Open connection on the network"""
    bl_idname = 'LNNetworkOpenConnectionNode'
    bl_label = 'Open Connection'
    arm_version = 1


    property0: HaxeEnumProperty(
        'property0',
        items = [('client', 'Client', 'Open client connection on network'),
                ('host', 'Host', 'Open host connection on the network'),
                ('securehost', 'Secure Host', 'Open secure host connection on the network')],
        name='', default='client')


    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Connection')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Connection')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
