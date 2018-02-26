import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

def remove_extra_inputs(self, context):
    # if not any(p == self.property0 for p in ['Or', 'And']):
    #     if len(self.inputs) > self.min_inputs:
    #         #FIXME: str(id(self)) gives us a key error here
    #         bpy.ops.arm.node_remove_input('EXEC_DEFAULT', node_index=str(id(self)))
    pass

class GateNode(Node, ArmLogicTreeNode):
    '''Gate node'''
    bl_idname = 'LNGateNode'
    bl_label = 'Gate'
    bl_icon = 'CURVE_PATH'
    property0 = EnumProperty(
        items = [('Equal', 'Equal', 'Equal'),
                 ('Not Equal', 'Not Equal', 'Not Equal'),
                 ('Greater', 'Greater', 'Greater'),
                 ('Greater Equal', 'Greater Equal', 'Greater Equal'),
                 ('Less', 'Less', 'Less'),
                 ('Less Equal', 'Less Equal', 'Less Equal'),
                 ('Or', 'Or', 'Or'),
                 ('And', 'And', 'And')],
        name='', default='Equal',
        update=remove_extra_inputs)
    min_inputs = 3
    
    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if any(p == self.property0 for p in ['Or', 'And']):
            row = layout.row(align=True)
            op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'ArmNodeSocketAction'
            op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))

add_node(GateNode, category='Logic')
