from arm.logicnode.arm_nodes import *

class ConcatenateStringNode(ArmLogicTreeNode):
    """Concatenates the given string."""
    bl_idname = 'LNConcatenateStringNode'
    bl_label = 'Concatenate String'
    arm_version = 1

    def __init__(self):
        super(ConcatenateStringNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Input 0')

        self.add_output('ArmStringSocket', 'String')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmStringSocket'
        op = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
