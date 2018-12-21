import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnSurfaceNode(Node, ArmLogicTreeNode):
    '''On surface node'''
    bl_idname = 'LNOnSurfaceNode'
    bl_label = 'On Surface'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Touched', 'Touched', 'Touched'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Touched')
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnSurfaceNode, category='Input')
