from arm.logicnode.arm_nodes import *

class SetNameNode(ArmLogicTreeNode):
    """Sets the name of the given object."""
    bl_idname = 'LNSetNameNode'
    bl_label = 'Set Object Name'
    arm_section = 'props'
    arm_version = 1

    def init(self, context):
        super(SetNameNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Name')
        self.add_output('ArmNodeSocketAction', 'Out')
