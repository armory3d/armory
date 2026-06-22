from arm.logicnode.arm_nodes import *

class SetFirstPersonControllerNode(ArmLogicTreeNode):
    """Config Visual"""
    bl_idname = 'LNSetFirstPersonControllerNode'
    bl_label = 'Set FirstPersonControllerSettings'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        
        """Config de la camara"""
        self.add_input('ArmFloatSocket', 'RotationSpeed')
        self.add_input('ArmFloatSocket', 'MaxPitch')
        self.add_input('ArmFloatSocket', 'MinPitch')

        self.add_input('ArmFloatSocket', 'MoveSpeed')
        self.add_input('ArmFloatSocket', 'RunSpeed')

        self.add_input('ArmBoolSocket', 'EnableJump')
        self.add_input('ArmBoolSocket', 'EnableAllowAirJump')
        self.add_input('ArmBoolSocket', 'EnableRun')
        self.add_input('ArmBoolSocket', 'EnableStamina')
        self.add_input('ArmBoolSocket', 'EnableFatigue') 

        self.add_output('ArmNodeSocketAction', 'Out')
