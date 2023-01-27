from arm.logicnode.arm_nodes import *


class ScreenToWorldSpaceNode(ArmLogicTreeNode):
    """Transforms the given screen coordinates into world coordinates."""
    bl_idname = 'LNScreenToWorldSpaceNode'
    bl_label = 'Screen to World Space'
    arm_section = 'matrix'
    arm_version = 1
    max_outputs = 8

    property0: HaxeBoolProperty('property0', name='Separator Out', default=False)

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Screen X')
        self.add_input('ArmIntSocket', 'Screen Y')

        self.add_output('ArmVectorSocket', 'World')
        self.add_output('ArmVectorSocket', 'Direction')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')  # Separator Out
        if self.property0:
            if len(self.outputs) < self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1])  # Direction vector
                self.add_output('ArmFloatSocket', 'X')  # World X
                self.add_output('ArmFloatSocket', 'Y')  # World Y
                self.add_output('ArmFloatSocket', 'Z')  # World Z
                self.add_output('ArmVectorSocket', 'Direction')  # Vector
                self.add_output('ArmFloatSocket', 'X')  # Direction X
                self.add_output('ArmFloatSocket', 'Y')  # Direction Y
                self.add_output('ArmFloatSocket', 'Z')  # Direction Z
        else:
            if len(self.outputs) == self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1])  # Z
                self.outputs.remove(self.outputs.values()[-1])  # Y
                self.outputs.remove(self.outputs.values()[-1])  # X
                self.outputs.remove(self.outputs.values()[-1])  # Direction
                self.outputs.remove(self.outputs.values()[-1])  # Z
                self.outputs.remove(self.outputs.values()[-1])  # Y
                self.outputs.remove(self.outputs.values()[-1])  # X
                self.add_output('ArmVectorSocket', 'Direction')
