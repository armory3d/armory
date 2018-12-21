import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorArrayNode(Node, ArmLogicTreeNode):
    '''Color array node'''
    bl_idname = 'LNArrayColorNode'
    bl_label = 'Array (Color)'
    bl_icon = 'QUESTION'

    def __init__(self):
        array_nodes[str(id(self))] = self
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketArray', 'Array')
        self.outputs.new('NodeSocketInt', 'Length')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketColor'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(ColorArrayNode, category='Array')
