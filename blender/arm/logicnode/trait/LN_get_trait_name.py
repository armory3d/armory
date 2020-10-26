from arm.logicnode.arm_nodes import *

class GetTraitNameNode(ArmLogicTreeNode):
    """Returns the name and the class type of the given trait."""
    bl_idname = 'LNGetTraitNameNode'
    bl_label = 'Get Trait Name'
    arm_version = 1

    def init(self, context):
        super(GetTraitNameNode, self).init(context)
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('NodeSocketString', 'Name')
        self.add_output('NodeSocketString', 'Class Type')

add_node(GetTraitNameNode, category=PKG_AS_CATEGORY)
