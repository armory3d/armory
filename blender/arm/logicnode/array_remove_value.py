import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayRemoveValueNode(Node, ArmLogicTreeNode):
    '''Array remove value node'''
    bl_idname = 'LNArrayRemoveValueNode'
    bl_label = 'Array Remove Value'
    bl_icon = 'QUESTION'

    # def __init__(self):
        # array_nodes[str(id(self))] = self

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Value')

    # def draw_buttons(self, context, layout):
    #     row = layout.row(align=True)

    #     op = row.operator('arm.node_add_input_value', text='New', icon='PLUS', emboss=True)
    #     op.node_index = str(id(self))
    #     op.socket_type = 'NodeSocketShader'
    #     op2 = row.operator('arm.node_remove_input_value', text='', icon='X', emboss=True)
    #     op2.node_index = str(id(self))

add_node(ArrayRemoveValueNode, category='Array')
