from arm.logicnode.arm_nodes import *

class GetPropertyNode(ArmLogicTreeNode):
    """Returns the value of the given object property.

    @seeNode Set Object Property"""
    bl_idname = 'LNGetPropertyNode'
    bl_label = 'Get Object Property'
    arm_version = 1
    arm_section = 'props'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Property')

        self.add_output('ArmDynamicSocket', 'Value')
        self.add_output('ArmStringSocket', 'Property')
