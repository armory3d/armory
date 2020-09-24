from arm.logicnode.arm_nodes import *

class SetPropertyNode(ArmLogicTreeNode):
    """Use to set the value of an object property."""
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
