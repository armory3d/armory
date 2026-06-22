from arm.logicnode.arm_nodes import *

class ArrayAddNode(ArmLogicTreeNode):
    """Adds the given value to the given array.

    @input Array: the array to manipulate.
    @input Modify Original: if `false`, the input array is copied before adding the value.
    @input Unique Values: if `true`, values may occur only once in that array (only primitive data types are supported).
    """
    bl_idname = 'LNArrayAddNode'
    bl_label = 'Array Add'
    arm_version = 5
    min_inputs = 6

    def __init__(self, *args, **kwargs):
        super(ArrayAddNode, self).__init__(*args, **kwargs)
        array_nodes[self.get_id_str()] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmBoolSocket', 'Modify Original', default_value=True)
        self.add_input('ArmBoolSocket', 'Unique Values')
        self.add_input('ArmBoolSocket', 'Add First')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Array')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input_value', text='Add Input', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmDynamicSocket'
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 4):
            raise LookupError()

        return NodeReplacement.Identity(self)
