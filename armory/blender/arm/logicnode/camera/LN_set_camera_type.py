from arm.logicnode.arm_nodes import *

class SetCameraTypeNode(ArmLogicTreeNode):
    """Sets the camera type."""
    bl_idname = 'LNSetCameraTypeNode'
    bl_label = 'Set Camera Type'
    arm_version = 1
    
    def remove_extra_inputs(self, context):
        while len(self.inputs) > 2:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Perspective':
            self.add_input('ArmFloatSocket', 'Fov')
            self.add_input('ArmFloatSocket', 'Start')
            self.add_input('ArmFloatSocket', 'End')
        if self.property0 == 'Orthographic':
            self.add_input('ArmFloatSocket', 'Scale')
    
    property0: HaxeEnumProperty(
    'property0',
    items = [('Perspective', 'Perspective', 'Perspective'),
             ('Orthographic', 'Orthographic', 'Orthographic')],
    name='', default='Perspective', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmFloatSocket', 'Fov')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')