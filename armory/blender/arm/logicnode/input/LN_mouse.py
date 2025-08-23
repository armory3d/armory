from arm.logicnode.arm_nodes import *


class MouseNode(ArmLogicTreeNode):
    """Activates the output on the given mouse event."""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    arm_section = 'mouse'
    arm_version = 3

    def update(self):
        if self.property0 != 'moved':
            self.label = f'{self.bl_label}: {self.property0} {self.property1}'
        else:
            self.label = f'{self.bl_label}: {self.property0}'


    def upd(self, context):
        if self.property0 != 'moved':
            self.label = f'{self.bl_label}: {self.property0} {self.property1}'
        else:
            self.label = f'{self.bl_label}: {self.property0}'


    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The mouse button begins to be pressed'),
                 ('down', 'Down', 'The mouse button is pressed'),
                 ('released', 'Released', 'The mouse button stops being pressed'),
                 ('moved', 'Moved', 'Moved')],
        name='', default='down', update=upd)
    property1: HaxeEnumProperty(
        'property1',
        items = [('left', 'Left', 'Left mouse button'),
                 ('middle', 'Middle', 'Middle mouse button'),
                 ('right', 'Right', 'Right mouse button'),
                 ('side1', 'Side 1', 'Side 1 mouse button'),
                 ('side2', 'Side 2', 'Side 2 mouse button')],
        name='', default='left', update=upd)
    property2: HaxeBoolProperty(
        'property2',
        name='Include Debug Console',
        description=(
            'If disabled, this node does not react to mouse press events'
            ' over the debug console area. Enable this option to catch those events'
        )
    )

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if self.property0 != 'moved':
            layout.prop(self, 'property1')
            layout.prop(self, 'property2')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property1}'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if 0 <= self.arm_version < 2:
            return NodeReplacement.Identity(self)

        elif self.arm_version == 2:
            return NodeReplacement(
                'LNMergedMouseNode', self.arm_version, 'LNMergedMouseNode', 3,
                in_socket_mapping={}, out_socket_mapping={0: 0, 1: 1},
                property_mapping={'property0': 'property0', 'property1': 'property1'},
                property_defaults={'property2': True}
            )

        raise LookupError()
