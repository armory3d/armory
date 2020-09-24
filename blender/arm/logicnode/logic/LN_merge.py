from arm.logicnode.arm_nodes import *

class MergeNode(ArmLogicTreeNode):
    """Runs the output when any connected input is running. The output execution will vary depending of inputs connected to it running."""
    bl_idname = 'LNMergeNode'
    bl_label = 'Merge'
    arm_version = 1

    def __init__(self):
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

add_node(MergeNode, category=PKG_AS_CATEGORY, section='flow')
