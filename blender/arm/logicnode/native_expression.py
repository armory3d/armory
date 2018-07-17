import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ExpressionNode(Node, ArmLogicTreeNode):
    '''Expression node'''
    bl_idname = 'LNExpressionNode'
    bl_label = 'Expression'
    bl_icon = 'GAME'
    min_inputs = 2
    @property
    def input_label(self):
        index = len(self.inputs)-2
        default = 'v{0}'.format(index)
        return default
    def __init__(self):
        array_nodes[str(id(self))] = self
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Expr')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Result')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketShader'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(ExpressionNode, category='Native')
