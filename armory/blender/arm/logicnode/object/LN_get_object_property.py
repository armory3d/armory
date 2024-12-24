from arm.logicnode.arm_nodes import *


class GetPropertyNode(ArmLogicTreeNode):
    """Return the value of the given object property. If the object is `null`
    or the property does not exist on the object, the node returns `null`.

    @input Object: The object to which the property belongs.
    @input Property: The name of the property from which to get the value.

    @output Value: The value of the property.
    @output Property: The name of the property as stated in the `Property` input.

    @see `Object Properties Panel > Armory Props > Properties` (do not confuse Armory object properties with Blender custom properties!)
    @see [`iron.object.Object.properties`](https://api.armory3d.org/iron/object/Object.html#properties)

    @seeNode Set Object Property
    """
    bl_idname = 'LNGetPropertyNode'
    bl_label = 'Get Object Property'
    arm_version = 1
    arm_section = 'props'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Property')

        self.add_output('ArmDynamicSocket', 'Value')
        self.add_output('ArmStringSocket', 'Property')
