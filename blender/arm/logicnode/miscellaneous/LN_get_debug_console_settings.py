from arm.logicnode.arm_nodes import *

class GetDebugConsoleSettings(ArmLogicTreeNode):
    """Returns the debug console settings."""
    bl_idname = 'LNGetDebugConsoleSettings'
    bl_label = 'Get Debug Console Settings'
    arm_version = 1

    def init(self, context):
        super(GetDebugConsoleSettings, self).init(context)
        self.add_output('ArmBoolSocket', 'Visible')
        self.add_output('ArmFloatSocket', 'Scale')
        self.add_output('ArmStringSocket', 'Position')
