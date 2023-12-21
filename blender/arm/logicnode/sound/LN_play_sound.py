import bpy

from arm.logicnode.arm_nodes import *


class PlaySoundNode(ArmLogicTreeNode):
    """Plays the given sound.

    @input Play: Plays the sound, or if paused, resumes the playback.
        The exact behaviour depends on the Retrigger option (see below).
    @input Pause: Pauses the playing sound. If no sound is playing,
        nothing happens.
    @input Stop: Stops the playing sound. If the playback is paused,
        this will reset the playback position to the start of the sound.
    @input Update Volume: Updates the volume of the current playback.
    @input Volume: Volume of the playback. Typically ranges from 0 to 1.

    @output Out: activated once when Play is activated.
    @output Running: activated while the playback is active.
    @output Done: activated when the playback has finished or was
        stopped manually.

    @option Sound/Sound Name: specify a sound by a resource or a string name
    @option Sound: The sound that will be played.
    @option Stream: Stream the sound from disk.
    @option Loop: Whether to loop the playback.
    @option Retrigger: If true, the playback position will be reset to
        the beginning on each activation of Play. If false, the playback
        will continue at the current position.
    @option Sample Rate: Manually override the sample rate of the sound
        (this controls the pitch and the playback speed).
    """
    bl_idname = 'LNPlaySoundRawNode'
    bl_label = 'Play Sound'
    bl_width_default = 200
    arm_version = 3

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 5:
            self.inputs.remove(self.inputs[-1])
        if self.property6 == 'Sound Name':
            self.add_input('ArmStringSocket', 'Sound Name')

    property0: HaxePointerProperty('property0', name='', type=bpy.types.Sound)
    
    property1: HaxeBoolProperty(
        'property1',
        name='Loop',
        description='Play the sound in a loop',
        default=False)
    property2: HaxeBoolProperty(
        'property2',
        name='Retrigger',
        description='Play the sound from the beginning every time',
        default=False)
    property3: HaxeBoolProperty(
        'property3',
        name='Use Custom Sample Rate',
        description='If enabled, override the default sample rate',
        default=False)
    property4: HaxeIntProperty(
        'property4',
        name='Sample Rate',
        description='Set the sample rate used to play this sound',
        default=44100,
        min=0)
    property5: HaxeBoolProperty(
        'property5',
        name='Stream',
        description='Stream the sound from disk',
        default=False
    )

    property6: HaxeEnumProperty(
    'property6',
    items = [('Sound', 'Sound', 'Sound'),
             ('Sound Name', 'Sound Name', 'Sound Name')],
    name='', default='Sound', update=remove_extra_inputs)

    def arm_init(self, context):

        self.add_input('ArmNodeSocketAction', 'Play')
        self.add_input('ArmNodeSocketAction', 'Pause')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmNodeSocketAction', 'Update Volume')
        self.add_input('ArmFloatSocket', 'Volume', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Is Running')
        self.add_output('ArmNodeSocketAction', 'Done')

    def draw_buttons(self, context, layout):
        
        layout.prop(self, 'property6')

        col = layout.column(align=True)
        
        if self.property6 == 'Sound':
            col.prop_search(self, 'property0', bpy.data, 'sounds', icon='NONE', text='')
        
        col.prop(self, 'property5')
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

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if 0 <= self.arm_version <= 2:
            return NodeReplacement.Identity(self)

        raise LookupError()
