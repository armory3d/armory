from arm.logicnode.arm_nodes import *

class DrawCurveNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawCurveNode'
    bl_label = 'Draw Curve'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Desativated', default_value = True)
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Strength')
        self.add_input('ArmIntSocket', 'Segments')
        self.add_input('ArmIntSocket', 'Start Point X')
        self.add_input('ArmIntSocket', 'Start Point Y')
        self.add_input('ArmIntSocket', 'Control Point 1 X')
        self.add_input('ArmIntSocket', 'Control Point 1 Y')
        self.add_input('ArmIntSocket', 'Control Point 2 X')
        self.add_input('ArmIntSocket', 'Control Point 2 Y')
        self.add_input('ArmIntSocket', 'End Point X')
        self.add_input('ArmIntSocket', 'End Point Y')
        
        self.add_output('ArmNodeSocketAction', 'Out')
        