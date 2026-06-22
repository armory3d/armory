from arm.logicnode.arm_nodes import *


class DistanceScreenToWorldSpaceNode(ArmLogicTreeNode):
    """Gets the distance from given screen coordinates to World coordinates.
    
    @input Screen X: screen x position.
    @input Screen Y: screen y position.
    @input At: World coordinates is a vector position.

    @output Distance At: distance result.
    """

    bl_idname = 'LNDistanceScreenToWorldSpaceNode'
    bl_label = 'Distance Screen to World Space'
    arm_section = 'matrix'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Screen X')
        self.add_input('ArmIntSocket', 'Screen Y')
        self.add_input('ArmVectorSocket', 'At')

        self.add_output('ArmFloatSocket', 'Distance at')