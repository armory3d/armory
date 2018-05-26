import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ConcatenateStringNode(Node, ArmLogicTreeNode):
    '''Concatenate string node'''
    bl_idname = 'LNConcatenateStringNode'
    bl_label = 'Concatenate String'
    bl_icon = 'CURVE_PATH'
    
    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Input 0')
        self.outputs.new('NodeSocketString', 'String')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketString'
        op = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))

add_node(ConcatenateStringNode, category='Value')
