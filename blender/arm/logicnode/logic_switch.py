import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SwitchNode(Node, ArmLogicTreeNode):
    '''Switch node'''
    bl_idname = 'LNSwitchNode'
    bl_label = 'Switch'
    bl_icon = 'CURVE_PATH'
    min_inputs = 1
    min_outputs = 1
    
    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Default')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input_output', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.in_socket_type = 'NodeSocketShader'
        op.out_socket_type = 'ArmNodeSocketAction'
        op.in_name_format = 'Case {0}'
        op.out_name_format = 'Case {0}'
        op.in_index_name_offset = -1
        op2 = row.operator('arm.node_remove_input_output', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(SwitchNode, category='Logic')
