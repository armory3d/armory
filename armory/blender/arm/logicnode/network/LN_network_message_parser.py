from arm.logicnode.arm_nodes import *


class NetworkMessageParserNode(ArmLogicTreeNode):
    """Parses message type from data packet"""
    bl_idname = 'LNNetworkMessageParserNode'
    bl_label = 'Message Parser'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('string', 'String', 'Event for a string over the network'),
                 ('vector', 'Vector', 'Event for a vector over the network'),
                 ('float', 'Float', 'Event for a float over the network'),
                 ('integer', 'Integer', 'Event for an integer over the network'),
                 ('boolean', 'Boolean', 'Event for a boolean over the network'),
                 ('transform', 'Transform', 'Event for a transform over the network'),
                 ('rotation', 'Rotation', 'Event for a rotation over the network')],
        name='', default='string')


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'API')
        self.add_input('ArmDynamicSocket', 'Data')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'API')
        self.add_output('ArmDynamicSocket', 'Data')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
