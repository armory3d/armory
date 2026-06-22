from arm.logicnode.arm_nodes import *


class MergeNode(ArmLogicTreeNode):
    """Activates the output when at least one connected input is activated.
    If multiple inputs are active, the behaviour is specified by the
    `Execution Mode` option.

    @output Active Input Index: [*Available if Execution Mode is set to
        Once Per Input*] The index of the last input that activated the output,
        -1 if there was no execution yet on the current frame.

    @option Execution Mode: The node's behaviour if multiple inputs are
        active on the same frame.
        - `Once Per Input`: If multiple inputs are active on one frame, activate
            the output for each active input individually (simple forwarding).
        - `Once Per Frame`: If multiple inputs are active on one frame,
            trigger the output only once.

    @option New: Add a new input socket.
    @option X Button: Remove the lowermost input socket."""
    bl_idname = 'LNMergeNode'
    bl_label = 'Merge'
    arm_section = 'flow'
    arm_version = 3
    min_inputs = 0

    def update_exec_mode(self, context):
        self.outputs['Active Input Index'].hide = self.property0 == 'once_per_frame'

    property0: HaxeEnumProperty(
        'property0',
        name='Execution Mode',
        description='The node\'s behaviour if multiple inputs are active on the same frame',
        items=[('once_per_input', 'Once Per Input',
                'If multiple inputs are active on one frame, activate the'
                ' output for each active input individually (simple forwarding)'),
               ('once_per_frame', 'Once Per Frame',
                'If multiple inputs are active on one frame, trigger the output only once')],
        default='once_per_input',
        update=update_exec_mode,
    )

    def __init__(self, *args, **kwargs):
        super(MergeNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmIntSocket', 'Active Input Index')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0', text='')

        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmNodeSocketAction'
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def draw_label(self) -> str:
        if len(self.inputs) == self.min_inputs:
            return self.bl_label

        return f'{self.bl_label}: [{len(self.inputs)}]'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()

        if self.arm_version == 1 or self.arm_version == 2:
            newnode = node_tree.nodes.new('LNMergeNode')
            newnode.property0 = self.property0

            # Recreate all original inputs
            array_nodes[str(id(newnode))] = newnode
            for idx, input in enumerate(self.inputs):
                bpy.ops.arm.node_add_input('EXEC_DEFAULT', node_index=str(id(newnode)), socket_type='ArmNodeSocketAction')

                for link in input.links:
                    node_tree.links.new(link.from_socket, newnode.inputs[idx])

            # Recreate outputs
            for link in self.outputs[0].links:
                node_tree.links.new(newnode.outputs[0], link.to_socket)

            return newnode