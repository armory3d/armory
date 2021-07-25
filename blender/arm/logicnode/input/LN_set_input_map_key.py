from arm.logicnode.arm_nodes import *

class SetInputMapKeyNode(ArmLogicTreeNode):
    """Set input map key."""
    bl_idname = 'LNSetInputMapKeyNode'
    bl_label = 'Set Input Map Key'
    arm_version = 1

    property0: EnumProperty(
        items = [('keyboard', 'Keyboard', 'Keyboard input'),
                 ('mouse', 'Mouse', 'Mouse input'),
                 ('gamepad', 'Gamepad', 'Gamepad input')],
        name='', default='keyboard')

    def init(self, context):
        super(SetInputMapKeyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Input Map')
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketFloat', 'Scale', default_value=1.0)
        self.add_input('NodeSocketFloat', 'Deadzone')
        self.add_input('NodeSocketInt', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')


    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')