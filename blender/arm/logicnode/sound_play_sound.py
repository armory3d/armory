import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlaySoundNode(Node, ArmLogicTreeNode):
    '''Play sound node'''
    bl_idname = 'LNPlaySoundRawNode'
    bl_label = 'Play Sound'
    bl_icon = 'QUESTION'

    property0: PointerProperty(name='', type=bpy.types.Sound)

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'sounds', icon='NONE', text='')

add_node(PlaySoundNode, category='Sound')
