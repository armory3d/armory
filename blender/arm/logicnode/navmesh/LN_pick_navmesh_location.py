from arm.logicnode.arm_nodes import *

class PickLocationNode(ArmLogicTreeNode):
    """Pick a location coordinates in the given NavMesh."""
    bl_idname = 'LNPickLocationNode'
    bl_label = 'Pick NavMesh Location'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'NavMesh')
        self.add_input('ArmVectorSocket', 'Screen Coords')

        self.add_output('ArmVectorSocket', 'Location')
