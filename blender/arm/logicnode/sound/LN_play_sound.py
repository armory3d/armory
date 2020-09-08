import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PlaySoundNode(ArmLogicTreeNode):
    """Play sound node"""
    bl_idname = 'LNPlaySoundRawNode'
    bl_label = 'Play Sound'
    bl_icon = 'NONE'

    property0: PointerProperty(name='', type=bpy.types.Sound)
    property1: BoolProperty(
        name='Loop',
        description='Play the sound in a loop',
        default=False)
    property2: BoolProperty(
        name='Retrigger',
        description='Play the sound from the beginning everytime',
        default=False)
    property3: BoolProperty(
        name='Use Custom Sample Rate',
        description='If enabled, override the default sample rate',
        default=False)
    property4: IntProperty(
        name='Sample Rate',
        description='Set the sample rate used to play this sound',
        default=44100,
        min=0)

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'Play')
        self.inputs.new('ArmNodeSocketAction', 'Pause')
        self.inputs.new('ArmNodeSocketAction', 'Stop')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketAction', 'Running')
        self.outputs.new('ArmNodeSocketAction', 'Done')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'sounds', icon='NONE', text='')

        col = layout.column(align=True)
        col.prop(self, 'property1')
        col.prop(self, 'property2')

        layout.label(text="Overrides:")
        # Sample rate
        split = layout.split(factor=0.15, align=False)
        split.prop(self, 'property3', text="")
        row = split.row()
        if not self.property3:
            row.enabled = False
        row.prop(self, 'property4')

add_node(PlaySoundNode, category=MODULE_AS_CATEGORY)
