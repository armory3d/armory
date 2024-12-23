from arm.logicnode.arm_nodes import *


class ObjectArrayNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores an array of object elements as a variable."""
    bl_idname = 'LNArrayObjectNode'
    bl_label = 'Array Object'
    arm_version = 3
    arm_section = 'variable'
    min_inputs = 0

    def __init__(self):
        super(ObjectArrayNode, self).__init__()
        self.register_id()

    def arm_init(self, context):
        self.add_output('ArmNodeSocketArray', 'Array', is_var=True)
        self.add_output('ArmIntSocket', 'Length')

    def draw_content(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmNodeSocketObject'
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def draw_label(self) -> str:
        if len(self.inputs) == self.min_inputs:
            return super().draw_label()

        return f'{super().draw_label()} [{len(self.inputs)}]'

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs.clear()
        for i in range(len(master_node.inputs)):
            inp = self.add_input('ArmNodeSocketObject', master_node.inputs[i].name)
            inp.hide = self.arm_logic_id != ''
            inp.enabled = self.arm_logic_id == ''
            inp.default_value_raw = master_node.inputs[i].default_value_raw

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
