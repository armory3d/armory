from arm.logicnode.arm_nodes import *

class WorldToScreenSpaceNode(ArmLogicTreeNode):
    """Transforms the given world coordinates into screen coordinates."""
    bl_idname = 'LNWorldToScreenSpaceNode'
    bl_label = 'World to Screen Space'
    arm_section = 'matrix'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'World')

        self.add_output('ArmVectorSocket', 'Screen')
