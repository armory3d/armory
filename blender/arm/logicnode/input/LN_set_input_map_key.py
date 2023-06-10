from arm.logicnode.arm_nodes import *

class SetInputMapKeyNode(ArmLogicTreeNode):
    """Set input map key."""
    bl_idname = 'LNSetInputMapKeyNode'
    bl_label = 'Set Input Map Key'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('keyboard', 'Keyboard', 'Keyboard input'),
                 ('mouse', 'Mouse', 'Mouse input'),
                 ('gamepad', 'Gamepad', 'Gamepad input')],
        name='', default='keyboard')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Input Map')
        self.add_input('ArmStringSocket', 'Key')
        self.add_input('ArmFloatSocket', 'Scale', default_value=1.0)
        self.add_input('ArmFloatSocket', 'Deadzone')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
