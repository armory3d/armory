from arm.logicnode.arm_nodes import *

class RaycastClosestObjectNode(ArmLogicTreeNode):
    """it takes an objects array and returns true of false if at least one of those objects is touched at screen (x, y), the object that is touched and the (x,y, z) position of that touch if returned"""
    bl_idname = 'LNRaycastClosestObjectNode'
    bl_label = 'Raycast Closest Object'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Obj Array')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmNodeSocketObject', 'Camera')
        
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
        self.add_output('ArmNodeSocketObject', 'Object')
        self.add_output('ArmVectorSocket', 'Location')
