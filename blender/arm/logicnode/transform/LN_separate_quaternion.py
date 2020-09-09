from arm.logicnode.arm_nodes import *


class SeparateQuaternionNode(ArmLogicTreeNode):

    bl_idname = 'LNSeparateQuaternionNode'
    bl_label = "Separate Quaternion"

    def init(self, context):
        self.add_input('NodeSocketVector', 'Quaternion')
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Z')
        self.add_output('NodeSocketFloat', 'W')


add_node(SeparateQuaternionNode, category=PKG_AS_CATEGORY, section='quaternions')
