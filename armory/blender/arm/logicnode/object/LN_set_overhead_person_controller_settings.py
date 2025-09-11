from arm.logicnode.arm_nodes import *

class SetOverheadPersonControllerNode(ArmLogicTreeNode):
    """Config Visual"""
    bl_idname = 'LNSetOverheadPersonControllerNode'
    bl_label = 'Set OverheadPersonControllerSettings'
    arm_section = 'props'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_input('ArmNodeSocketObject', 'Object')

        """Suavizado"""
        self.add_input('ArmBoolSocket', 'EnableSmoothTrack')
        self.add_input('ArmFloatSocket', 'SmoothSpeed')

        self.add_input('ArmFloatSocket', 'MoveSpeed')
        self.add_input('ArmFloatSocket', 'RunSpeed')

        self.add_input('ArmBoolSocket', 'EnableJump')
        self.add_input('ArmBoolSocket', 'EnableAllowAirJump')
        self.add_input('ArmBoolSocket', 'EnableRun')
        self.add_input('ArmBoolSocket', 'EnableStamina')
        self.add_input('ArmBoolSocket', 'EnableFatigue') 

        self.add_output('ArmNodeSocketAction', 'Out')
