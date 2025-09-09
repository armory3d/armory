from arm.logicnode.arm_nodes import *

class SequenceNode(ArmLogicTreeNode):
    """Activates the outputs one by one sequentially and repeatedly."""
    bl_idname = 'LNSequenceNode'
    bl_label = 'Output Sequence'
    arm_section = 'flow'
    arm_version = 2
    min_outputs = 0

    def __init__(self, *args, **kwargs):
        super(SequenceNode, self).__init__(*args, **kwargs)
        array_nodes[self.get_id_str()] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_output', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmNodeSocketAction'
        column = row.column(align=True)
        op = column.operator('arm.node_remove_output', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.outputs) == self.min_outputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
