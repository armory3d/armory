from arm.logicnode.arm_nodes import *

class GetParentNode(ArmLogicTreeNode):
    """Returns the direct parent (nearest in the hierarchy) of the given object.

    @seeNode Set Object Parent"""
    bl_idname = 'LNGetParentNode'
    bl_label = 'Get Object Parent'
    arm_section = 'relations'
    arm_version = 1

    def init(self, context):
        super(GetParentNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Child')

        self.add_output('ArmNodeSocketObject', 'Parent')
