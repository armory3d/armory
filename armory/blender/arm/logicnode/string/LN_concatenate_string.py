from arm.logicnode.arm_nodes import *

class ConcatenateStringNode(ArmLogicTreeNode):
    """Concatenates the given string."""
    bl_idname = 'LNConcatenateStringNode'
    bl_label = 'Concatenate String'
    arm_version = 2
    min_inputs = 1

    def __init__(self, *args, **kwargs):
        super(ConcatenateStringNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Input 0')

        self.add_output('ArmStringSocket', 'String')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmStringSocket'
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
