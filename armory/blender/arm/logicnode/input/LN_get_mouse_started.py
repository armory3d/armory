from arm.logicnode.arm_nodes import *


class GetMouseStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetMouseStartedNode'
    bl_label = 'Get Mouse Started'
    arm_version = 2

    property0: HaxeBoolProperty(
        'property0',
        name='Include Debug Console',
        description=(
            'If disabled, this node does not react to mouse press events'
            ' over the debug console area. Enable this option to catch those events'
        )
    )

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'Button')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNGetMouseStartedNode', self.arm_version, 'LNGetMouseStartedNode', 2,
            in_socket_mapping={0: 0}, out_socket_mapping={0: 0, 1: 1},
            property_defaults={'property0': True}
        )
