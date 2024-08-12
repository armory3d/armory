try:
    from bpy.types import NodeSocketInterfaceInt
except:
    from bpy.types import NodeTreeInterfaceSocketInt
from arm.logicnode.arm_nodes import *

class SelectNode(ArmLogicTreeNode):
    """Selects one of multiple values (of arbitrary types) based on some
    input state. The exact behaviour of this node is specified by the
    `Execution Mode` option (see below).

    @output Out: [*Available if Execution Mode is set to From Input*]
        Activated after the node was executed.

    @output Value: The last selected value. This value is not reset
        until the next execution of this node.

    @option Execution Mode: Specifies the condition that determines
        what value to choose.
        - `From Index`: Select the value at the given index. If there is
            no value at that index, the value plugged in to the
            `Default` input is used instead (`null` if unconnected).
        - `From Input`: This mode uses input pairs of one action socket
            and one value socket. Depending on which action socket is
            activated, the associated value socket (the value with the
            same index as the activated action input) is forwarded to
            the `Value` output.

    @option New: Add a new value to the list of values.
    @option X Button: Remove the value with the highest index."""
    bl_idname = 'LNSelectNode'
    bl_label = 'Select'
    arm_version = 2
    min_inputs = 2

    def update_exec_mode(self, context):
        self.set_mode()

    property0: HaxeEnumProperty(
        'property0',
        name='Execution Mode',
        description="The node's behaviour.",
        items=[
            ('from_index', 'From Index', 'Choose the value from the given index'),
            ('from_input', 'From Input', 'Choose the value with the same position as the active input')],
        default='from_index',
        update=update_exec_mode,
    )

    # The number of choices, NOT of individual inputs. This needs to be
    # a property in order to be saved with each individual node
    num_choices: IntProperty(default=1, min=0)

    def __init__(self):
        super().__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.set_mode()

    def set_mode(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.property0 == 'from_index':
            self.add_input('ArmIntSocket', 'Index')
            self.add_input('ArmDynamicSocket', 'Default')
            self.num_choices = 0

        # from_input
        else:
            # We could also start with index 1 here, but we need to use
            # 0 for the "from_index" mode and it makes the code simpler
            # if we stick to the same convention for both exec modes
            self.add_input('ArmNodeSocketAction', 'Input 0')
            self.add_input('ArmDynamicSocket', 'Value 0')
            self.num_choices = 1

            self.add_output('ArmNodeSocketAction', 'Out')

        self.add_output('ArmDynamicSocket', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0', text='')

        row = layout.row(align=True)
        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_input_func'

        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_input_func'
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def add_input_func(self):
        if self.property0 == 'from_input':
            self.add_input('ArmNodeSocketAction', f'Input {self.num_choices}')

            # Move new action input up to the end of all other action inputs
            self.inputs.move(from_index=len(self.inputs) - 1, to_index=self.num_choices)

        self.add_input('ArmDynamicSocket', f'Value {self.num_choices}')

        self.num_choices += 1

    def remove_input_func(self):
        if self.property0 == 'from_input':
            if len(self.inputs) > self.min_inputs:
                self.inputs.remove(self.inputs[self.num_choices - 1])

        if len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices}]'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
