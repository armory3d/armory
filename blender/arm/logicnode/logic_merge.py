import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MergeNode(Node, ArmLogicTreeNode):
    '''Merge node'''
    bl_idname = 'LNMergeNode'
    bl_label = 'Merge'
    bl_icon = 'QUESTION'

    def __init__(self):
        array_nodes[str(id(self))] = self
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmNodeSocketAction'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(MergeNode, category='Logic')
