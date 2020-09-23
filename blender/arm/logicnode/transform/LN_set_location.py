from arm.logicnode.arm_nodes import *

class SetLocationNode(ArmLogicTreeNode):
    """Use to set the location of an object."""
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Location'
    arm_version = 1

    def init(self, context):
        super(SetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Location')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetLocationNode, category=PKG_AS_CATEGORY, section='location')
