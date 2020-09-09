from arm.logicnode.arm_nodes import *

class VectorArrayNode(ArmLogicTreeNode):
    """Vector array node"""
    bl_idname = 'LNArrayVectorNode'
    bl_label = 'Array Vector'

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        self.add_output('ArmNodeSocketArray', 'Array', is_var=True)
        self.add_output('NodeSocketInt', 'Length')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketVector'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(VectorArrayNode, category=PKG_AS_CATEGORY, section='variable')
