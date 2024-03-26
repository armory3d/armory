from arm.logicnode.arm_nodes import *


class NetworkCloseConnectionNode(ArmLogicTreeNode):
    """Close connection on the network"""
    bl_idname = 'LNNetworkCloseConnectionNode'
    bl_label = 'Close Connection'
    arm_version = 1


    property0: HaxeBoolProperty(
        'property0',
        name="To Null",
        description="Close the connection and set to null",
        default=False)


    property1: HaxeEnumProperty(
        'property1',
        items = [('client', 'Client', 'Close client connection on network'),
                ('host', 'Host', 'Close host connection on the network'),
                ('securehost', 'Secure Host', 'Close secure host connection on the network')],
        name='', default='client')


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Connection')

        self.add_output('ArmNodeSocketAction', 'Out')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
