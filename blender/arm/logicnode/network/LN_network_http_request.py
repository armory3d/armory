from arm.logicnode.arm_nodes import *


class NetworkHttpRequestNode(ArmLogicTreeNode):
    """Network Http Request"""
    bl_idname = 'LNNetworkHttpRequestNode'
    bl_label = 'Http Request'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('post', 'Post', 'Http post request'),
                 ('get', 'Get', 'Http get request')],
        name='', default='post')

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Request')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Status')
        self.add_output('ArmDynamicSocket', 'Response')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
