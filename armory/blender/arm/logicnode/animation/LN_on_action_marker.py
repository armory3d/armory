from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(ArmLogicTreeNode):
    """Activates the output when the object action reaches the action marker."""
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Marker')

        self.add_output('ArmNodeSocketAction', 'Out')
