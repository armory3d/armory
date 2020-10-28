from arm.logicnode.arm_nodes import *

class ArrayNode(ArmLogicTreeNode):
    """Stores the given array as a variable."""
    bl_idname = 'LNArrayNode'
    bl_label = 'Array Dynamic'
    arm_version = 1
    arm_section = 'variable'

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(ArrayNode, self).init(context)
        self.add_output('ArmNodeSocketArray', 'Array', is_var=True)
        self.add_output('NodeSocketInt', 'Length')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketShader'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
