from arm.logicnode.arm_nodes import *

class GetDebugConsoleSettings(ArmLogicTreeNode):
    """Returns the debug console settings."""
    bl_idname = 'LNGetDebugConsoleSettings'
    bl_label = 'Get Debug Console Settings'
    arm_version = 1

    def init(self, context):
        super(GetDebugConsoleSettings, self).init(context)
        self.add_output('NodeSocketBool', 'Visible')
        self.add_output('NodeSocketFloat', 'Scale')
        self.add_output('NodeSocketString', 'Position')
