import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RpShadowQualityNode(Node, ArmLogicTreeNode):
    '''Configure shadow quality node'''
    bl_idname = 'LNRpShadowQualityNode'
    bl_label = 'Rp Shadow Quality'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('High', 'High', 'High'),
                 ('Medium', 'Medium', 'Medium'),
                 ('Low', 'Low', 'Low')
                 ],
        name='', default='Medium')
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(RpShadowQualityNode, category='Renderpath')