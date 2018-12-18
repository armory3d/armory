import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TraitNode(Node, ArmLogicTreeNode):
    '''Trait node'''
    bl_idname = 'LNTraitNode'
    bl_label = 'Trait'
    bl_icon = 'QUESTION'

    property0: StringProperty(name='', default='')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Trait')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(TraitNode, category='Variable')
