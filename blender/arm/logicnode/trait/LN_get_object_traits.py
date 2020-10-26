from arm.logicnode.arm_nodes import *

class GetObjectTraitsNode(ArmLogicTreeNode):
    """Returns all traits from the given object."""
    bl_idname = 'LNGetObjectTraitsNode'
    bl_label = 'Get Object Traits'
    arm_version = 1

    def init(self, context):
        super(GetObjectTraitsNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketArray', 'Traits')

add_node(GetObjectTraitsNode, category=PKG_AS_CATEGORY)
