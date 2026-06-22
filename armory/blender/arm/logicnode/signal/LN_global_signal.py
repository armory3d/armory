from arm.logicnode.arm_nodes import *


class GlobalSignalNode(ArmLogicTreeNode):
    """Gets or creates a global Signal by name.

    Global Signals are stored in a static registry and can be accessed from
    any logic tree in the scene. Provide a unique name to identify the signal.

    Use this for communication between different objects or logic trees without
    needing to pass Signal references directly.

    @seeNode Signal
    @seeNode On Signal
    @seeNode Emit Signal"""

    bl_idname = 'LNGlobalSignalNode'
    bl_label = 'Global Signal'
    arm_version = 1
    arm_section = 'signal'


    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Property')
        self.add_output('ArmDynamicSocket', 'Signal')