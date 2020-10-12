from arm.logicnode.arm_nodes import *

class MergeNode(ArmLogicTreeNode):
    """Activates the output when any connected input is activated.

    @option New: Add a new input socket.
    @option X Button: Remove the lowermost input socket."""
    bl_idname = 'LNMergeNode'
    bl_label = 'Merge'
    arm_section = 'flow'
    arm_version = 1

    def __init__(self):
        super(MergeNode, self).__init__()
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(MergeNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmNodeSocketAction'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
