from arm.logicnode.arm_nodes import *

class SetLocationNode(ArmLogicTreeNode):
    """Sets the location of the given object."""
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Object Location'
    arm_section = 'location'
    arm_version = 1

    def init(self, context):
        super(SetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Location')

        self.add_output('ArmNodeSocketAction', 'Out')
