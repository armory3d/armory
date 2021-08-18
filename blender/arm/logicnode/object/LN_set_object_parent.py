from arm.logicnode.arm_nodes import *

class SetParentNode(ArmLogicTreeNode):
    """Sets the direct parent (nearest in the hierarchy) of the given object.

    @seeNode Get Object Parent"""
    bl_idname = 'LNSetParentNode'
    bl_label = 'Set Object Parent'
    arm_section = 'relations'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent', default_value='Parent')

        self.add_output('ArmNodeSocketAction', 'Out')
