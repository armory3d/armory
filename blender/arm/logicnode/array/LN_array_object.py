from arm.logicnode.arm_nodes import *


class ObjectArrayNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores an array of object elements as a variable."""
    bl_idname = 'LNArrayObjectNode'
    bl_label = 'Array Object'
    arm_version = 1
    arm_section = 'variable'

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
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = self.get_id_str()

    def draw_label(self) -> str:
        if len(self.inputs) == 0:
            return super().draw_label()

        return f'{super().draw_label()} [{len(self.inputs)}]'

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs.clear()
        for i in range(len(master_node.inputs)):
            inp = self.add_input('ArmNodeSocketObject', master_node.inputs[i].name)
            inp.hide = self.arm_logic_id != ''
            inp.enabled = self.arm_logic_id == ''
            inp.default_value_raw = master_node.inputs[i].default_value_raw
