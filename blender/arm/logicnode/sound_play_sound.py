import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlaySoundNode(Node, ArmLogicTreeNode):
    """Play sound node"""
    bl_idname = 'LNPlaySoundRawNode'
    bl_label = 'Play Sound'
    bl_icon = 'PLAY_SOUND'

    property0: PointerProperty(name='', type=bpy.types.Sound)
    property1: BoolProperty(
        name='Loop',
        description='Play the sound in a loop',
        default=False)
    property2: BoolProperty(
        name='Use Custom Sample Rate',
        description='If enabled, override the default sample rate',
        default=False)
    property3: IntProperty(
        name='Sample Rate',
        description='Set the sample rate used to play this sound',
        default=44100,
        min=0)

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'sounds', icon='NONE', text='')

        layout.prop(self, 'property1')

        layout.label(text="Overrides:")
        # Sample rate
        split = layout.split(factor=0.15, align=False)
        split.prop(self, 'property2', text="")
        row = split.row()
        if not self.property2:
            row.enabled = False
        row.prop(self, 'property3')

add_node(PlaySoundNode, category='Sound')
