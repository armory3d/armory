from arm.logicnode.arm_nodes import *

class QuaternionNode(ArmLogicTreeNode):
    """Quaternion node"""
    bl_idname = 'LNQuaternionNode'
    bl_label = 'Quaternion'
    arm_version = 1

    def init(self, context):
        super(QuaternionNode, self).init(context)
        self.add_input('NodeSocketFloat', 'X')
        self.add_input('NodeSocketFloat', 'Y')
        self.add_input('NodeSocketFloat', 'Z')
        self.add_input('NodeSocketFloat', 'W', default_value=1.0)

        self.add_output('NodeSocketVector', 'Quaternion')
        self.add_output('NodeSocketVector', 'XYZ')
        self.add_output('NodeSocketFloat', 'W')

add_node(QuaternionNode, category=PKG_AS_CATEGORY, section='quaternions')
