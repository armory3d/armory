import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SurfaceNode(Node, ArmLogicTreeNode):
    '''Surface node'''
    bl_idname = 'LNMergedSurfaceNode'
    bl_label = 'Surface'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Touched', 'Touched', 'Touched'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Touched')
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(SurfaceNode, category='Input')
