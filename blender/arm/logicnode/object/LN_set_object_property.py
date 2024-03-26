from arm.logicnode.arm_nodes import *


class SetPropertyNode(ArmLogicTreeNode):
    """Set the value of the given object property.

    This node can be used to share variables between different traits.
    If the trait(s) you want to access the variable with are on
    different objects, use the *[`Global Object`](#global-object)*
    node to store the data. Every trait can access this one.

    @input Object: The object to which the property belongs. If the object is `null`, the node does not do anything.
    @input Property: The name of the property from which to get the value.
    @input Value: The value of the property.

    @see `Object Properties Panel > Armory Props > Properties` (do not confuse Armory object properties with Blender custom properties!)
    @see [`iron.object.Object.properties`](https://api.armory3d.org/iron/object/Object.html#properties)

    @seeNode Get Object Property
    """
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
