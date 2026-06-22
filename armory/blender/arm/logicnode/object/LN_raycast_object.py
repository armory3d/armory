from arm.logicnode.arm_nodes import *

class RaycastObjectNode(ArmLogicTreeNode):
    """it takes an object and returns true or false if the object is touched at screen (x, y) and the (x,y, z) position of that touch if returned"""
    bl_idname = 'LNRaycastObjectNode'
    bl_label = 'Raycast Object'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmNodeSocketObject', 'Camera')
        
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
        self.add_output('ArmVectorSocket', 'Location')

