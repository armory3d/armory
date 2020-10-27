from arm.logicnode.arm_nodes import *

class BooleanNode(ArmLogicTreeNode):
    """Stores the given boolean as a variable. A boolean value has just two
    states: `True` and `False`."""
    bl_idname = 'LNBooleanNode'
    bl_label = 'Boolean'
    arm_version = 1

    def init(self, context):
        super(BooleanNode, self).init(context)
        self.add_input('NodeSocketBool', 'Bool In')
        self.add_output('NodeSocketBool', 'Bool Out', is_var=True)
