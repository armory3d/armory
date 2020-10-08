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
    arm_version = 1

    def init(self, context):
        super(SetPropertyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetPropertyNode, category=PKG_AS_CATEGORY, section='props')
