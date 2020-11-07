from arm.logicnode.arm_nodes import *

class SetDebugConsoleSettings(ArmLogicTreeNode):
    """Sets the debug console settings."""
    bl_idname = 'LNSetDebugConsoleSettings'
    bl_label = 'Set Debug Console Settings'
    arm_version = 1

    property0: EnumProperty(
        items = [('Left', 'Left', 'Left'),
                 ('Center', 'Center', 'Center'),
                 ('Right', 'Right', 'Right')],
        name='', default='Right')

    def init(self, context):  
        super(SetDebugConsoleSettings, self).init(context) 
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Visible')  
        self.add_input('NodeSocketFloat', 'Scale')  
        self.inputs[-1].default_value = 1.0
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
