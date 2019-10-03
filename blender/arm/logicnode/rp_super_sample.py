import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RpSuperSampleNode(Node, ArmLogicTreeNode):
    '''Configure super sampling node'''
    bl_idname = 'LNRpSuperSampleNode'
    bl_label = 'Rp Super-sampling'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('1', '1', '1'),
                 ('1.5', '1.5', '1.5'),
                 ('2', '2', '2'),
                 ('4', '4', '4')
                 ],
        name='', default='1')
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(RpSuperSampleNode, category='Renderpath')