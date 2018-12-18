import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

def remove_extra_inputs(self, context):
    if not any(p == self.property0 for p in ['Or', 'And']):
        while len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])

class GateNode(Node, ArmLogicTreeNode):
    '''Gate node'''
    bl_idname = 'LNGateNode'
    bl_label = 'Gate'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Equal', 'Equal', 'Equal'),
                 ('Almost Equal', 'Almost Equal', 'Almost Equal'),
                 ('Greater', 'Greater', 'Greater'),
                 ('Greater Equal', 'Greater Equal', 'Greater Equal'),
                 ('Less', 'Less', 'Less'),
                 ('Less Equal', 'Less Equal', 'Less Equal'),
                 ('Or', 'Or', 'Or'),
                 ('And', 'And', 'And')],
        name='', default='Equal',
        update=remove_extra_inputs)
    min_inputs = 3
    property1: FloatProperty(name='Tolerance', description='Precision for float compare', default=0.0001)
    
    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'True')
        self.outputs.new('ArmNodeSocketAction', 'False')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if self.property0 == 'Almost Equal':
            layout.prop(self, 'property1')

        if any(p == self.property0 for p in ['Or', 'And']):
            row = layout.row(align=True)
            op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'NodeSocketShader'
            op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))

add_node(GateNode, category='Logic')
