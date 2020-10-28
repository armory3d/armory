from arm.logicnode.arm_nodes import *

class ConcatenateStringNode(ArmLogicTreeNode):
    """Concatenates the given string."""
    bl_idname = 'LNConcatenateStringNode'
    bl_label = 'Concatenate String'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(ConcatenateStringNode, self).init(context)
        self.add_input('NodeSocketString', 'Input 0')
        self.add_output('NodeSocketString', 'String')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketString'
        op = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
