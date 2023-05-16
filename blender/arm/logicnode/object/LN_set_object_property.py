from arm.logicnode.arm_nodes import *

class SetPropertyNode(ArmLogicTreeNode):
    """Sets the value of the given object property.

    This node can be used to share variables between different traits.
    If the trait(s) you want to access the variable with are on
    different objects, use the *[`Global Object`](#global-object)*
    node to store the data. Every trait can access this one.

    @seeNode Get Object Property"""
    bl_idname = 'LNSetPropertyNode'
    bl_label = 'Set Object Property'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Property')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
