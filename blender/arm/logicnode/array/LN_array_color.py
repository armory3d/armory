from arm.logicnode.arm_nodes import *

class ColorArrayNode(ArmLogicTreeNode):
    """Stores an array of color elements as a variable."""
    bl_idname = 'LNArrayColorNode'
    bl_label = 'Array Color'
    arm_version = 1
    arm_section = 'variable'

    def __init__(self):
        super(ColorArrayNode, self).__init__()
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(ColorArrayNode, self).init(context)
        self.add_output('ArmNodeSocketArray', 'Array', is_var=True)
        self.add_output('NodeSocketInt', 'Length')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketColor'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
