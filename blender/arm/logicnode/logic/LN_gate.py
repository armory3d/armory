from arm.logicnode.arm_nodes import *


def remove_extra_inputs(self, context):
    if not any(p == self.property0 for p in ['Or', 'And']):
        while len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])
    if self.property0 == 'Between':
        self.add_input('ArmDynamicSocket', 'Input 3')

class GateNode(ArmLogicTreeNode):
    """Logic nodes way to do "if" statements. When activated, it
    compares if its two inputs are being Equal, Greater Equal,
    Less Equal, Not Equal, or Between, regardless of variable type, and passes
    through its active input to the output that matches the result of
    the comparison.

    "And" and "Or" are being used for booleans only, and pass through
    the input when both booleans are true (And) or at least one (Or)."""
    bl_idname = 'LNGateNode'
    bl_label = 'Gate'
    arm_version = 3
    min_inputs = 3

    property0: HaxeEnumProperty(
        'property0',
        items = [('Equal', 'Equal', 'Equal'),
                 ('Not Equal', 'Not Equal', 'Not Equal'),
                 ('Almost Equal', 'Almost Equal', 'Almost Equal'),
                 ('Greater', 'Greater', 'Greater'),
                 ('Greater Equal', 'Greater Equal', 'Greater Equal'),
                 ('Less', 'Less', 'Less'),
                 ('Less Equal', 'Less Equal', 'Less Equal'),
                 ('Between', 'Between', 'Input 1 Between Input 2 and Input 3 inclusive'),
                 ('Or', 'Or', 'Or'),
                 ('And', 'And', 'And')],
        name='', default='Equal',
        update=remove_extra_inputs)
    property1: HaxeFloatProperty('property1', name='Tolerance', description='Precision for float compare', default=0.0001)

    def __init__(self):
        super(GateNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Input 1')
        self.add_input('ArmDynamicSocket', 'Input 2')

        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if self.property0 == 'Almost Equal':
            layout.prop(self, 'property1')

        if any(p == self.property0 for p in ['Or', 'And']):
            row = layout.row(align=True)
            op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'ArmDynamicSocket'
            column = row.column(align=True)
            op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            if len(self.inputs) == self.min_inputs:
                column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()
            
        if self.arm_version == 1 or self.arm_version == 2:
            return NodeReplacement(
                'LNGateNode', self.arm_version, 'LNGateNode', 2,
                in_socket_mapping={0:0, 1:1, 2:2}, out_socket_mapping={0:0, 1:1}
            )