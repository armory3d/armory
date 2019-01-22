import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GroupNode(Node, ArmLogicTreeNode):
    '''Group node'''
    bl_idname = 'LNGroupNode'
    bl_label = 'Collection'
    bl_icon = 'QUESTION'

    property0: PointerProperty(name='', type=bpy.types.Collection)
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketArray', 'Array')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'collections', icon='NONE', text='')

add_node(GroupNode, category='Variable')
