from arm.logicnode.arm_nodes import *

class SnapshotNode(ArmLogicTreeNode):
    """Stores the given value snapshot whether activated."""
    bl_idname = 'LNSnapshotNode'
    bl_label = 'Snapshot'
    arm_version = 1

    def init(self, context):
        super(SnapshotNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Snapshot')

add_node(SnapshotNode, category=PKG_AS_CATEGORY)
