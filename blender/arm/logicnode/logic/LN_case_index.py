from bpy.types import NodeSocketInterfaceInt
from arm.logicnode.arm_nodes import *

class CaseIndexNode(ArmLogicTreeNode):
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
    bl_idname = 'LNCaseIndexNode'
    bl_label = 'Case Index'
    arm_version = 1
    min_inputs = 2

    def update_exec_mode(self, context):
        self.set_mode()

    num_choices: IntProperty(default=1, min=0)

    def __init__(self):
        super().__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.set_mode()

    def set_mode(self):
  
        self.add_input('ArmDynamicSocket', 'Dynamic')
        self.num_choices = 0

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
        self.add_input('ArmDynamicSocket', f'Value {self.num_choices}')

        self.num_choices += 1

    def remove_input_func(self):
        if len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices-1}]'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
