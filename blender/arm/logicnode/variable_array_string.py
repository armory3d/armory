import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StringArrayNode(Node, ArmLogicTreeNode):
    '''String array node'''
    bl_idname = 'LNArrayStringNode'
    bl_label = 'Array (String)'
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
        op.socket_type = 'NodeSocketString'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(StringArrayNode, category='Array')
